"""Incremental result retention; page byte limits apply before accumulation."""

from __future__ import annotations

import json
from dataclasses import asdict

from batten.storage import KeyEntry, ListEntry, ListPage, StorageError


class PageBuffer:
    def __init__(self, maximum: int, detail: str):
        self.maximum, self.detail = maximum, detail
        self.items: list[KeyEntry | ListEntry] = []
        self.prefixes: list[str] = []
        self.retained = len(json.dumps(asdict(ListPage((), (), "0" * 32))).encode())

    def append(self, key: str, is_directory: bool) -> bool:
        entry = KeyEntry(key) if self.detail == "keys" else ListEntry(key)
        encoded = json.dumps(key + "/" if is_directory else asdict(entry))
        size = len(encoded.encode()) + 2
        if self.retained + size > self.maximum:
            if not self.items and not self.prefixes:
                raise StorageError("limit_exceeded")
            return False
        self.retained += size
        if is_directory:
            self.prefixes.append(key + "/")
        else:
            self.items.append(entry)
        return True
