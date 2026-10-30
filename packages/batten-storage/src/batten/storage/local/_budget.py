"""Shared provider resource reservations, released idempotently across workers."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from batten.storage import StorageError


class Budget:
    def __init__(self, maximum: int):
        self.maximum = maximum
        self.used = 0
        self.lock = Lock()

    def reserve(self) -> Reservation:
        with self.lock:
            if self.used >= self.maximum:
                raise StorageError("limit_exceeded")
            self.used += 1
        return Reservation(self)


@dataclass
class Reservation:
    budget: Budget
    active: bool = True

    def release(self) -> None:
        with self.budget.lock:
            if self.active:
                self.active = False
                self.budget.used -= 1
