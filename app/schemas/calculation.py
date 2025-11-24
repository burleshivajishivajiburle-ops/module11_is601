"""Pydantic models for calculator input and output validation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import CalculationType


class CalculationBase(BaseModel):
    """Shared fields for all calculation payloads."""

    a: float = Field(..., description="First operand", examples=[10.5])
    b: float = Field(..., description="Second operand", examples=[4])
    type: CalculationType = Field(..., description="Operation", examples=["add"])

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        return CalculationType.from_value(value)

    @model_validator(mode="after")
    def validate_operands(self) -> "CalculationBase":
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"a": 10, "b": 5, "type": "add"}},
    )


class CalculationCreate(CalculationBase):
    """Input schema for creating calculations."""

    user_id: Optional[UUID] = Field(
        default=None,
        description="Optional UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class CalculationRead(CalculationBase):
    """Output schema for returning stored calculations."""

    id: UUID = Field(..., description="Primary key")
    user_id: Optional[UUID] = Field(default=None, description="Owning user")
    result: float = Field(..., description="Computed result", examples=[15])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "a": 10,
                "b": 5,
                "type": "add",
                "result": 15,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )
