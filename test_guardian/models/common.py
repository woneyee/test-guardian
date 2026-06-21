"""Shared model helpers."""

from enum import StrEnum


class StrictStrEnum(StrEnum):
    """String enum with readable values in serialized output."""

    def __str__(self) -> str:
        return self.value
