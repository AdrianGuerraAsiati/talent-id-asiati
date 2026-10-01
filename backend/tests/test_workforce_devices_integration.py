from collections.abc import Generator

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from talent_id.main import app
from talent_id.shared.config import Settings, get_settings
from talent_id.shared.db import Base, get_session


def build_client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    def override_session() -> Generator[Session, None, None]:
        with testing_session() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def override_settings() -> Settings:
        return Settings(internal_api_key=SecretStr("integration-secret"))

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = override_settings
    return TestClient(app)


def test_workforce_and_device_vertical_slice() -> None:
    client = build_client()
    internal_headers = {"X-Internal-Key": "integration-secret"}

    site_response = client.post(
        "/v1/workforce/sites",
        headers=internal_headers,
        json={
            "name": "Bogota HQ",
            "code": "BOG-HQ",
            "timezone": "America/Bogota",
        },
    )
    assert site_response.status_code == 201
    site_id = site_response.json()["id"]

    schedule_response = client.post(
        "/v1/workforce/schedules",
        headers=internal_headers,
        json={
            "name": "Administrative",
            "start_time": "08:30:00",
            "end_time": "18:00:00",
            "tolerance_minutes": 10,
        },
    )
    assert schedule_response.status_code == 201
    schedule_id = schedule_response.json()["id"]

    employee_response = client.put(
        "/v1/workforce/employees/talent-employee-001",
        headers=internal_headers,
        json={
            "display_name": "Integration Employee",
            "status": "active",
            "site_id": site_id,
            "schedule_id": schedule_id,
            "attendance_eligible": True,
        },
    )
    assert employee_response.status_code == 200
    assert employee_response.json()["external_employee_id"] == "talent-employee-001"

    provision_response = client.post(
        "/v1/devices",
        headers=internal_headers,
        json={
            "site_id": site_id,
            "name": "Reception Tablet 01",
        },
    )
    assert provision_response.status_code == 201
    provisioned = provision_response.json()
    device_id = provisioned["id"]
    device_secret = provisioned["device_secret"]

    kiosk_response = client.get(
        "/v1/kiosk/context",
        headers={
            "X-Device-Id": device_id,
            "X-Device-Secret": device_secret,
        },
    )
    assert kiosk_response.status_code == 200
    assert kiosk_response.json()["site_name"] == "Bogota HQ"
    assert kiosk_response.json()["device"]["id"] == device_id

    revoke_response = client.post(
        f"/v1/devices/{device_id}/revoke",
        headers=internal_headers,
    )
    assert revoke_response.status_code == 200
    assert revoke_response.json()["active"] is False

    rejected_response = client.get(
        "/v1/kiosk/context",
        headers={
            "X-Device-Id": device_id,
            "X-Device-Secret": device_secret,
        },
    )
    assert rejected_response.status_code == 401

    app.dependency_overrides.clear()
