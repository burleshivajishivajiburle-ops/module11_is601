"""Integration tests for the calculation Pydantic schemas."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.enums import CalculationType
from app.schemas.calculation import CalculationBase, CalculationCreate, CalculationRead


def test_calculation_base_accepts_valid_payload():
    """Happy-path payload should serialize to floats and enum members."""

    payload = {"a": 10, "b": 4, "type": "ADD"}

    schema = CalculationBase(**payload)

    assert schema.a == pytest.approx(10.0)
    assert schema.b == pytest.approx(4.0)
    assert schema.type is CalculationType.ADD


def test_calculation_base_rejects_unknown_type():
    """Unknown operation labels should raise a validation error."""

    with pytest.raises(ValidationError, match="Unsupported calculation type"):
        CalculationBase(a=1, b=2, type="modulus")


def test_calculation_base_division_by_zero_guard():
    """Zero denominators must be rejected at validation time."""

    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationBase(a=4, b=0, type="divide")


def test_calculation_base_allows_zero_numerator():
    """Division with a zero numerator remains valid."""

    schema = CalculationBase(a=0, b=5, type="divide")

    assert schema.a == 0
    assert schema.b == 5


def test_calculation_create_accepts_optional_user():
    """user_id defaults to None when omitted."""

    schema = CalculationCreate(a=2, b=3, type="add")

    assert schema.user_id is None


def test_calculation_create_casts_uuid_strings():
    """UUID strings should convert to UUID objects."""

    user_id = uuid4()

    schema = CalculationCreate(a=2, b=3, type="add", user_id=str(user_id))

    assert schema.user_id == user_id


def test_calculation_read_round_trips_all_fields():
    """CalculationRead should expose all persisted attributes."""

    payload = {
        "id": uuid4(),
        "user_id": uuid4(),
        "a": 9,
        "b": 3,
        "type": CalculationType.DIVIDE,
        "result": 3.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    schema = CalculationRead(**payload)

    assert schema.id == payload["id"]
    assert schema.user_id == payload["user_id"]
    assert schema.result == pytest.approx(3.0)
    assert schema.type is CalculationType.DIVIDE


def test_enum_choices_utility_returns_expected_values():
    """choices helper should return the enum values tuple."""

    assert CalculationType.choices() == (
        "add",
        "subtract",
        "multiply",
        "divide",
    )

