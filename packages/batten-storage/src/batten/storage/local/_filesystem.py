"""Descriptor-relative managed namespace; no path resolution followed by open."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import stat
import threading
import time
import uuid
from collections.abc import Generator
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any as JSONAny
from typing import cast

from batten.storage import Absent, Condition, Limits, Matches, ObjectInfo, StorageError

from ._budget import Budget
from ._scope import Attempt

try:
    import fcntl
except ImportError:
    fcntl = None

JSONMap = dict[str, JSONAny]


def identifier(value: str) -> str:
    if not re.fullmatch("[a-f0-9]{32}", value):
        raise StorageError("invalid_request")
    return value


def keys(key: str, limits: Limits) -> list[str]:
    if not key or any(ord(c) < 32 or ord(c) == 127 for c in key):
        raise StorageError("invalid_key")
    parts = key.split("/")
    if any(p in {"", ".", ".."} or "\\" in p or ":" in p for p in parts):
        raise StorageError("invalid_key")
    try:
        lengths = [len(part.encode("utf-8")) for part in parts]
    except UnicodeError:
        raise StorageError("invalid_key") from None
    if (
        sum(lengths) + len(parts) - 1 > limits.max_key_bytes
        or len(parts) > limits.max_depth
    ):
        raise StorageError("limit_exceeded")
    if any(length > 120 for length in lengths):
        raise StorageError("invalid_key")
    return [part.encode().hex() for part in parts]


def directory(parent: int, name: str, create: bool = False) -> int:
    if create:
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent)
        except FileExistsError:
            pass
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    info = os.fstat(fd)
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        os.close(fd)
        raise StorageError("invalid_request")
    return fd


def regular(parent: int, name: str, flags: int = os.O_RDONLY) -> int:
    fd = os.open(name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
    info = os.fstat(fd)
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or info.st_uid != os.getuid()
    ):
        os.close(fd)
        raise StorageError("invalid_request")
    return fd


def load(parent: int, name: str, maximum: int) -> JSONMap:
    fd = regular(parent, name)
    try:
        data = os.read(fd, maximum + 1)
        if len(data) > maximum:
            raise StorageError("limit_exceeded")
        value = json.loads(data)
        if not isinstance(value, dict):
            raise StorageError("io_failure")
        return cast(JSONMap, value)
    finally:
        os.close(fd)


def save(
    parent: int, name: str, value: JSONMap, maximum: int, attempt: Attempt | None = None
) -> None:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    if len(data) > maximum:
        raise StorageError("limit_exceeded")
    temporary = "t" + uuid.uuid4().hex
    fd = regular(parent, temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(data)
        if attempt is not None:
            attempt.effect = "unknown"
        os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary, dir_fd=parent)


def initialize_sync(root: Path) -> None:
    if not root.is_absolute() or fcntl is None or not hasattr(os, "O_NOFOLLOW"):
        raise StorageError("unsupported")
    root.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        with os.scandir(fd) as entries:
            if next(entries, None) is not None:
                raise StorageError("invalid_request")
        for name in ("objects", "blobs", "uploads"):
            os.mkdir(name, mode=0o700, dir_fd=fd)
        os.close(regular(fd, "lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        save(fd, "identity", {"id": uuid.uuid4().hex}, 4096)
    finally:
        os.close(fd)


class Filesystem:
    def __init__(self, root: Path, limits: Limits):
        self.root = root
        self.limits = limits
        self.fd = -1
        self.objects = -1
        self.blobs = -1
        self.uploads = -1
        self.prefix = ""
        self.budget = Budget(limits.max_active_transfers)

    def prepare(self) -> None:
        if fcntl is None or not hasattr(os, "O_NOFOLLOW"):
            raise StorageError("unsupported")
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        info = os.fstat(self.fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise StorageError("invalid_request")
        identity = identifier(load(self.fd, "identity", 4096)["id"])
        self.objects = directory(self.fd, "objects")
        self.blobs = directory(self.fd, "blobs")
        self.uploads = directory(self.fd, "uploads")
        profile = hashlib.sha256(
            json.dumps(asdict(self.limits), sort_keys=True).encode()
        ).hexdigest()
        self.prefix = identity + "." + profile

    @contextlib.contextmanager
    def locked(self) -> Generator[None]:
        if fcntl is None:
            raise StorageError("unsupported")
        fd = regular(self.fd, "lock", os.O_RDWR)
        try:
            deadline = time.monotonic() + self.limits.operation_timeout_ms / 1000
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise StorageError("timeout") from None
                    threading.Event().wait(remaining / self.limits.max_retry_attempts)
            yield
        finally:
            os.close(fd)

    @contextlib.contextmanager
    def parent(self, key: str, create: bool = False) -> Generator[tuple[int, str]]:
        parts = keys(key, self.limits)
        fd = os.dup(self.objects)
        try:
            for part in parts[:-1]:
                try:
                    probe = regular(fd, "o" + part)
                except FileNotFoundError:
                    probe = -1
                if probe != -1:
                    os.close(probe)
                    raise StorageError("path_conflict")
                child = directory(fd, "d" + part, create)
                os.close(fd)
                fd = child
            yield fd, "o" + parts[-1]
        finally:
            os.close(fd)

    def record(self, key: str) -> JSONMap | None:
        try:
            with self.parent(key) as (fd, name):
                value = load(fd, name, self.limits.max_transfer_buffer_bytes)
                identifier(value["blob"])
                identifier(value["revision"])
                if value["key"] != key:
                    raise StorageError("io_failure")
                return value
        except FileNotFoundError:
            return None

    def info(self, value: JSONMap) -> ObjectInfo:
        key: str = value["key"]
        token = ".".join((
            self.prefix,
            hashlib.sha256(key.encode()).hexdigest(),
            value["revision"],
        ))
        return ObjectInfo(key, value["size"], value["modified"], token)

    def condition(self, value: JSONMap | None, condition: Condition) -> None:
        if isinstance(condition, Absent) and value is not None:
            raise StorageError("precondition_failed")
        if isinstance(condition, Matches):
            if value is None or condition.version != self.info(value).version:
                raise StorageError("precondition_failed")

    def publish(
        self, key: str, blob: str, size: int, condition: Condition, attempt: Attempt
    ) -> ObjectInfo:
        with self.locked():
            previous = self.record(key)
            self.condition(previous, condition)
            with self.parent(key, create=True) as (fd, name):
                try:
                    child = directory(fd, "d" + name[1:])
                except FileNotFoundError:
                    child = -1
                if child >= 0:
                    os.close(child)
                    raise StorageError("path_conflict")
                value = {
                    "key": key,
                    "blob": identifier(blob),
                    "size": size,
                    "revision": uuid.uuid4().hex,
                    "modified": datetime.now(timezone.utc).isoformat(),
                }
                save(fd, name, value, self.limits.max_transfer_buffer_bytes, attempt)
                if previous is not None:
                    with contextlib.suppress(FileNotFoundError):
                        os.unlink(identifier(previous["blob"]), dir_fd=self.blobs)
                return self.info(value)

    def close(self) -> None:
        for name in ("uploads", "blobs", "objects", "fd"):
            fd = getattr(self, name)
            if fd >= 0:
                os.close(fd)
                setattr(self, name, -1)
