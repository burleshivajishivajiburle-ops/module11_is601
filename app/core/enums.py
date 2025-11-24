"""Domain enumerations used across the application."""
from __future__ import annotations

from enum import Enum


class CalculationType(str, Enum):
    """Supported calculation types for the calculator domain."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

    @classmethod
    def from_value(cls, value: str | "CalculationType") -> "CalculationType":
        """Normalize arbitrary strings into the canonical enum values."""
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError("Calculation type must be provided as a string.")
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(
            f"Unsupported calculation type '{value}'."
            f" Use one of: {', '.join(member.value for member in cls)}."
        )

    @classmethod
    def choices(cls) -> tuple[str, ...]:
        """Return the tuple of valid string representations."""
        return tuple(member.value for member in cls)
