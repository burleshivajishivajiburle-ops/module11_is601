"""Domain enumerations shared across the calculator app."""
from __future__ import annotations

from enum import Enum


class CalculationType(str, Enum):
    """Supported calculation operations."""

    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

    @classmethod
    def from_value(cls, value: str | "CalculationType") -> "CalculationType":
        """Normalize an incoming string into a CalculationType member."""
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError("Calculation type must be a string.")
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(
            f"Unsupported calculation type '{value}'."
            f" Valid options: {', '.join(member.value for member in cls)}."
        )

    @classmethod
    def choices(cls) -> tuple[str, ...]:
        """Return a tuple of the valid string values."""
        return tuple(member.value for member in cls)
