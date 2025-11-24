Assignment SQLAlchemy Calculator
================================

Overview
--------
- FastAPI service that persists calculator requests via SQLAlchemy and validates payloads with Pydantic v2.
- `Calculation` model stores operands `a` and `b`, the operation `type`, the computed `result`, and an optional `user_id` foreign key.
- A reusable `CalculationFactory` (see `app/models/calculation.py`) encapsulates the operation mapping.
- Tests cover arithmetic helpers, Pydantic schemas, SQLAlchemy integration, and Playwright-powered end-to-end flows.

Requirements
------------
- Python 3.10+
- Node.js is not required (Playwright is installed via Python package)
- PostgreSQL 15+ for parity with CI (SQLite can be used locally if desired)
- Docker (optional for container builds)

Initial Setup
-------------
1. Clone the repository and create a virtual environment.
2. Install dependencies:

	 ```bash
	 pip install --upgrade pip
	 pip install -r requirements.txt
	 ```

3. Install Playwright browser binaries (required once):

	 ```bash
	 python -m playwright install
	 python -m playwright install winldd  # Windows only
	 ```

4. Configure the database URL. By default `settings.DATABASE_URL` points at a Postgres container. Override as needed:

	 ```bash
	 export DATABASE_URL="postgresql://user:password@localhost:5432/calculator_db"
	 # or for SQLite while developing:
	 export DATABASE_URL="sqlite:///./local.db"
	 ```

Running The Application
-----------------------

```bash
uvicorn main:app --reload
```

The HTML calculator lives at `http://127.0.0.1:8000/`.

Testing
-------
- Ensure the `DATABASE_URL` points at a reachable database (SQLite is fine).
- Windows users should set a local coverage file to avoid UNC locking:

	```powershell
	$env:COVERAGE_FILE = "$HOME/.coverage"
	```

- Run the full suite (unit, integration, e2e) with coverage:

	```bash
	pytest
	```

- Narrow scopes when debugging:

	```bash
	pytest tests/unit
	pytest tests/integration -k calculation
	pytest tests/e2e --headed  # inspect Playwright interactions
	```

Database Integration Test Notes
--------------------------------
- Integration tests expect the database schema to exist. Apply migrations or let SQLAlchemy create tables before running.
- For Postgres in Docker:

	```bash
	docker compose up -d db
	alembic upgrade head  # if migrations exist
	pytest
	```

CI/CD Pipeline
--------------
- `.github/workflows/test.yml` spins up PostgreSQL, installs dependencies, runs pytest (unit, integration, e2e), scans the Docker image with Trivy, then builds and pushes container images on `master` pushes.
- Ensure the following GitHub secrets are configured for deploy:
	- `DOCKERHUB_USERNAME`
	- `DOCKERHUB_TOKEN`

Docker
------
Build locally:

```bash
docker build -t shivajiburle/asignmentsqlaa:local .
```

Run the container:

```bash
docker run --rm -p 8000:8000 shivajiburle/asignmentsqlaa:local
```

The CI pipeline publishes multi-arch images to Docker Hub:
- `https://hub.docker.com/r/shivajiburle/asignmentsqlaa`

Additional Documentation
------------------------
- Reflection notes: `REFLECTION.md`
- SQLAlchemy models: `app/models`
- Pydantic schemas: `app/schemas`
- Test suites: `tests/unit`, `tests/integration`, `tests/e2e`

