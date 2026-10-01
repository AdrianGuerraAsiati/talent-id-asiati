# Talent ID

Talent ID is ASIATI's employee identity, attendance and recognition platform. It connects reception kiosks with Talent Intelligence so attendance, punctuality and employee rewards can be managed from one ecosystem.

## Product scope

- Android reception kiosk for facial check-in/check-out.
- Multi-site attendance.
- Biometric enrollment and recognition through AWS Rekognition.
- Offline fallback methods such as PIN/QR.
- Talent Points ledger and reward redemptions.
- Integration with Talent Intelligence as the HR source of truth.
- Auditable administrative actions.

## Architecture

Talent ID starts as a **modular monolith**: one backend deployable with strong internal module boundaries.

```text
Android Kiosk
    |
    v
Talent ID API
    |
    +-- workforce
    +-- devices
    +-- biometrics
    +-- attendance
    +-- rewards
    +-- integrations
    +-- audit
    |
    +-- PostgreSQL
    +-- AWS Rekognition
    +-- Talent Intelligence
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for architectural rules and module boundaries.

## Repository layout

```text
backend/     FastAPI modular monolith
android/     Native Android kiosk application
infra/       AWS infrastructure definitions
docs/        Architecture decisions and technical documentation
```

## Backend stack

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Pytest
- Ruff

## Local backend

PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn talent_id.main:app --reload
```

Start local PostgreSQL from the repository root:

```powershell
docker compose up -d postgres
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

## First delivery milestones

1. Architecture/bootstrap.
2. Workforce sync from Talent Intelligence.
3. Device registration and site assignment.
4. Biometric enrollment.
5. Facial attendance check-in/check-out.
6. Attendance dashboard integration with Talent.
7. Talent Points.
8. Rewards catalog/redemptions.
9. Multi-site rollout.

## Architectural rule

A module may use another module only through its public application contract or domain event. Direct access to another module's repositories or tables is not allowed.
