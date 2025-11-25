# Module 11 Reflection

## Highlights
- Rebuilt the SQLAlchemy `Calculation` model to store primitive operands (`a`, `b`) plus the computed `result`, which simplified persistence and aligns with the assignment rubric.
- Introduced a shared `CalculationType` enum and `CalculationFactory` to keep validation logic centralized and reusable across the API, schemas, and database layer.
- Strengthened automated testing: unit tests verify arithmetic helpers and Pydantic validation, integration tests hit SQLAlchemy + Pydantic together, and Playwright drives the UI against a live FastAPI server.

## Challenges
- Balancing developer ergonomics with CI requirements: the integration tests now default to SQLite for local runs but seamlessly point to GitHub Actions' Postgres service via `DATABASE_URL`/`TEST_DATABASE_URL`.
- Updating legacy tests and documentation without regressing existing behavior required careful sequencing (models → schemas → tests → CI configs).

## Lessons Learned
- Centralizing enumerations avoids drift between the ORM, schemas, and business logic.
- Lightweight factories keep calculations deterministic and make it trivial to extend the operation set later.
- Investing in layered tests (unit + integration + e2e) paid off immediately by catching schema/model drift during the refactor.
