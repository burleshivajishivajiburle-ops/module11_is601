"""SQLAlchemy model and factory helpers for calculator data."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Callable, Dict, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.core.enums import CalculationType
from app.database import Base
from app.operations import add, divide, multiply, subtract


class Calculation(Base):
    """Persisted representation of an arithmetic calculation."""

    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(32), nullable=False, index=True)
    result = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="calculations", passive_deletes=True)

    @validates("type")
    def _validate_type(self, key, value):  # pragma: no cover - exercised via tests
        calc_type = CalculationType.from_value(value)
        return calc_type.value

    @validates("a", "b")
    def _validate_numbers(self, key, value):  # pragma: no cover - exercised via tests
        if value is None:
            raise ValueError(f"{key} is required")
        return float(value)

    def compute_result(self) -> float:
        """Compute and persist the result based on the stored operands."""
        calc_type = CalculationType.from_value(self.type)
        operation = CalculationFactory.operation_map()[calc_type]
        if calc_type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero.")
        self.result = float(operation(self.a, self.b))
        return self.result

    def __repr__(self):  # pragma: no cover - debug helper
        return (
            f"<Calculation id={self.id} type={self.type} a={self.a}"
            f" b={self.b} result={self.result}>"
        )


class CalculationFactory:
    """Factory that builds Calculation instances with validated results."""

    _OPERATIONS: Dict[CalculationType, Callable[[float, float], float]] = {
        CalculationType.ADD: add,
        CalculationType.SUBTRACT: subtract,
        CalculationType.MULTIPLY: multiply,
        CalculationType.DIVIDE: divide,
    }

    @classmethod
    def operation_map(cls) -> Dict[CalculationType, Callable[[float, float], float]]:
        """Expose the operation mapping for reuse in tests."""
        return cls._OPERATIONS

    @classmethod
    def create(
        cls,
        *,
        a: float,
        b: float,
        calculation_type: str | CalculationType,
        user_id: Optional[uuid.UUID] = None,
    ) -> Calculation:
        """Construct a Calculation populated with the computed result."""

        calc_type = CalculationType.from_value(calculation_type)
        if calc_type == CalculationType.DIVIDE and b == 0:
            raise ValueError("Cannot divide by zero.")
        operation = cls._OPERATIONS[calc_type]
        result = float(operation(a, b))
        return Calculation(
            user_id=user_id,
            a=float(a),
            b=float(b),
            type=calc_type.value,
            result=result,
        )
