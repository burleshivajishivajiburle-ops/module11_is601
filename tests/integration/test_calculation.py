"""Integration tests covering the scalar Calculation model and factory."""

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.enums import CalculationType
from app.database import Base
from app.models.calculation import Calculation, CalculationFactory


def test_calculation_instantiation_normalizes_fields():
    """Ensure SQLAlchemy validators coerce operands and type."""

    calc = Calculation(a="3", b=4, type="ADD")

    assert calc.a == pytest.approx(3.0)
    assert calc.b == pytest.approx(4.0)
    assert calc.type == CalculationType.ADD.value


@pytest.mark.parametrize(
    ("operation", "a", "b", "expected"),
    [
        ("add", 10, 5, 15),
        (CalculationType.SUBTRACT, 10, 4, 6),
        ("MuLtIpLy", 3, 7, 21),
        (CalculationType.DIVIDE, 20, 5, 4),
    ],
)
def test_factory_produces_calculation_with_result(operation, a, b, expected):
    """Factory should normalize type, compute result, and keep operands as floats."""

    user_id = uuid4()

    calculation = CalculationFactory.create(
        a=a,
        b=b,
        calculation_type=operation,
        user_id=user_id,
    )

    assert isinstance(calculation, Calculation)
    assert calculation.user_id == user_id
    assert calculation.a == pytest.approx(float(a))
    assert calculation.b == pytest.approx(float(b))
    assert calculation.type == CalculationType.from_value(operation).value
    assert calculation.result == pytest.approx(expected)


def test_factory_prevents_division_by_zero():
    """Division by zero should fail fast before creating the model."""

    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculationFactory.create(a=10, b=0, calculation_type="divide")


def test_compute_result_updates_instance():
    """compute_result should reuse stored operands and persist result."""

    calc = Calculation(a=6, b=7, type=CalculationType.MULTIPLY.value, result=None)

    value = calc.compute_result()

    assert value == pytest.approx(42)
    assert calc.result == pytest.approx(42)


def test_compute_result_division_by_zero():
    """Stored calculations must also guard against zero division."""

    calc = Calculation(a=2, b=0, type=CalculationType.DIVIDE.value)

    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.compute_result()


def test_operation_map_exposes_expected_functions():
    """Expose arithmetic helpers to tests for coverage and inspection."""

    operation_map = CalculationFactory.operation_map()

    assert set(operation_map.keys()) == set(CalculationType)
    # Spot-check one operation to ensure mapping is correct.
    assert operation_map[CalculationType.ADD](2, 3) == 5


@pytest.fixture(scope="module")
def db_engine():
    """Provision a database engine against the configured test database."""

    database_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

    if not database_url or "Microsoft.PowerShell.Core" in database_url:
        database_url = "sqlite+pysqlite:///:memory:"

    if database_url.startswith("sqlite") and ":memory:" in database_url:
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    elif database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Yield a transactional SQLAlchemy session for each database test."""

    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


def test_calculation_persists_and_round_trips(db_session):
    """The database should store operands, type, and result for later retrieval."""

    calc = CalculationFactory.create(a=8, b=3, calculation_type="subtract")
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    stored = db_session.get(Calculation, calc.id)

    assert stored is not None
    assert stored.a == pytest.approx(8.0)
    assert stored.b == pytest.approx(3.0)
    assert stored.type == CalculationType.SUBTRACT.value
    assert stored.result == pytest.approx(5.0)


def test_database_session_blocks_invalid_type(db_session):
    """Model validation should reject unsupported operations before persistence."""

    with pytest.raises(ValueError, match="Unsupported calculation type"):
        calc = Calculation(a=1, b=1, type="modulus")
        db_session.add(calc)
        db_session.flush()

