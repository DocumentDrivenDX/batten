"""Bounded, persistent managed upload records and original completion receipts."""

from __future__ import annotations

import contextlib
import os
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

from batten.storage import (
    Absent,
    Any,
    Condition,
    Digest,
    Matches,
    ObjectInfo,
    PartReceipt,
    StorageError,
    TransferVerification,
    UploadInfo,
    UploadRef,
    WriteReceipt,
)

from ._filesystem import Filesystem, JSONMap, identifier, load, save


def condition(value: JSONMap) -> Condition:
    choices = {"any": Any, "absent": Absent}
    if value["kind"] == "matches":
        return Matches(value["version"])
    return choices[value["kind"]]()


def part(value: JSONMap) -> PartReceipt:
    digest = Digest(**value["digest"]) if value["digest"] else None
    return PartReceipt(
        UploadRef(value["upload"]["id"]),
        value["part_number"],
        value["size_bytes"],
        value["token"],
        digest,
    )


def receipt(value: JSONMap | None) -> WriteReceipt | None:
    if value is None:
        return None
    verification = value["verification"]
    verified = (
        TransferVerification(Digest(**verification["digest"]), verification["scope"])
        if verification
        else None
    )
    return WriteReceipt(ObjectInfo(**value["info"]), verified)


class UploadState:
    def __init__(self, fs: Filesystem):
        self.fs = fs

    def read(
        self, upload: UploadRef, identity: str, allow_expired: bool = False
    ) -> JSONMap:
        try:
            value = load(
                self.fs.uploads,
                identifier(upload.id),
                self.fs.limits.max_transfer_buffer_bytes,
            )
        except (FileNotFoundError, StorageError):
            raise StorageError("upload_invalid") from None
        if value["owner"] != identity or value["profile"] != self.fs.prefix:
            raise StorageError("denied")
        if value["expiry"] <= time.time():
            if not allow_expired:
                raise StorageError("upload_expired")
            value["state"] = "expired"
        return value

    def save(self, upload: UploadRef, value: JSONMap) -> None:
        save(
            self.fs.uploads,
            identifier(upload.id),
            value,
            self.fs.limits.max_transfer_buffer_bytes,
        )

    def begin(
        self,
        key: str,
        identity: str,
        expected: Digest | None,
        requested: Condition,
        origin: str,
        resumable: bool,
    ) -> UploadInfo:
        with self.fs.locked():
            try:
                registry: JSONMap = load(
                    self.fs.uploads,
                    "registry",
                    self.fs.limits.max_transfer_buffer_bytes,
                )
            except FileNotFoundError:
                registry = {"sessions": []}
            sessions: list[str] = registry["sessions"]
            self._expire(sessions)
            save(
                self.fs.uploads,
                "registry",
                registry,
                self.fs.limits.max_transfer_buffer_bytes,
            )
            if len(sessions) >= self.fs.limits.max_retained_uploads:
                raise StorageError("limit_exceeded")
            active = sum(
                load(
                    self.fs.uploads, reference, self.fs.limits.max_transfer_buffer_bytes
                )["state"]
                not in {"complete", "aborted", "expired"}
                for reference in sessions
            )
            if active >= self.fs.limits.max_active_uploads:
                raise StorageError("limit_exceeded")
            upload = UploadRef(uuid.uuid4().hex)
            value: JSONMap = {
                "key": key,
                "owner": identity,
                "origin": origin,
                "resumable": resumable,
                "profile": self.fs.prefix,
                "condition": asdict(requested),
                "digest": asdict(expected) if expected else None,
                "expiry": time.time() + self.fs.limits.upload_ttl_seconds,
                "state": "open",
                "parts": {},
                "parts_revision": uuid.uuid4().hex,
                "busy": {},
                "receipt": None,
                "manifest": None,
            }
            self.save(upload, value)
            sessions.append(upload.id)
            save(
                self.fs.uploads,
                "registry",
                registry,
                self.fs.limits.max_transfer_buffer_bytes,
            )
            return self.info(upload, value)

    def _expire(self, sessions: list[str]) -> None:
        for upload in tuple(sessions):
            try:
                value = load(
                    self.fs.uploads,
                    identifier(upload),
                    self.fs.limits.max_transfer_buffer_bytes,
                )
            except FileNotFoundError:
                sessions.remove(upload)
                continue
            if value["expiry"] > time.time():
                continue
            for entry in value["parts"].values():
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(identifier(entry["token"]), dir_fd=self.fs.blobs)
            for pending in value["busy"].values():
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(identifier(pending), dir_fd=self.fs.blobs)
            os.unlink(upload, dir_fd=self.fs.uploads)
            sessions.remove(upload)

    def info(self, upload: UploadRef, value: JSONMap) -> UploadInfo:
        expiry = datetime.fromtimestamp(value["expiry"], timezone.utc).isoformat()
        return UploadInfo(
            upload,
            value["state"],
            1,
            self.fs.limits.max_part_bytes,
            self.fs.limits.max_parts,
            expiry,
            receipt(value["receipt"]),
        )

    def claim(self, upload: UploadRef, identity: str, number: int) -> JSONMap:
        with self.fs.locked():
            value = self.read(upload, identity)
            if value["state"] != "open" or str(number) in value["busy"]:
                raise StorageError("upload_conflict")
            if len(value["busy"]) >= self.fs.limits.max_parallel_parts:
                raise StorageError("limit_exceeded")
            value["busy"][str(number)] = uuid.uuid4().hex
            self.save(upload, value)
            return value

    def release(
        self,
        upload: UploadRef,
        identity: str,
        number: int,
        accepted: PartReceipt | None,
    ) -> None:
        with self.fs.locked():
            value = self.read(upload, identity)
            pending = value["busy"].pop(str(number), None)
            previous = None
            keep = accepted is not None and value["state"] == "open"
            if keep and accepted is not None:
                previous = value["parts"].get(str(number))
                value["parts"][str(number)] = asdict(accepted)
                value["parts_revision"] = uuid.uuid4().hex
            if value["state"] == "aborting" and not value["busy"]:
                value["state"] = "aborted"
            self.save(upload, value)
            discard = previous["token"] if previous else None
            if not keep:
                discard = pending
            if discard:
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(identifier(discard), dir_fd=self.fs.blobs)
            if accepted is not None and not keep:
                raise StorageError("upload_conflict")
