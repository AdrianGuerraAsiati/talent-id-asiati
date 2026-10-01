from collections.abc import Generator
from uuid import UUID

from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from talent_id.main import app
from talent_id.modules.biometrics.dependencies import get_biometric_provider
from talent_id.modules.biometrics.domain import EnrollmentResult, RecognitionMatch
from talent_id.shared.config import Settings, get_settings
from talent_id.shared.db import Base, get_session


class FakeBiometricProvider:
    provider_name = "fake_biometrics"

    def __init__(self) -> None:
        self.provider_user_id: str | None = None
        self.enroll_calls = 0
        self.recognize_calls = 0

    def enroll(self, *, provider_user_id: str, image_bytes: bytes) -> EnrollmentResult:
        assert image_bytes
        self.enroll_calls += 1
        self.provider_user_id = provider_user_id
        return EnrollmentResult(
            provider_user_id=provider_user_id,
            face_ids=("fake-face-001",),
        )

    def recognize(
        self,
        *,
        image_bytes: bytes,
        threshold: float,
    ) -> RecognitionMatch | None:
        assert image_bytes
        assert threshold == 98
        self.recognize_calls += 1
        if self.provider_user_id is None:
            return None
        return RecognitionMatch(
            provider_user_id=self.provider_user_id,
            similarity=99.4,
        )


def build_client(provider: FakeBiometricProvider) -> TestClient:
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
        return Settings(
            internal_api_key=SecretStr("integration-secret"),
            rekognition_match_threshold=98,
        )

    def override_provider() -> FakeBiometricProvider:
        return provider

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_biometric_provider] = override_provider
    return TestClient(app)


def test_enrollment_recognition_attendance_and_retry() -> None:
    provider = FakeBiometricProvider()
    client = build_client(provider)
    internal_headers = {"X-Internal-Key": "integration-secret"}

    try:
        site = client.post(
            "/v1/workforce/sites",
            headers=internal_headers,
            json={
                "name": "Bogota HQ",
                "code": "BOG-HQ",
                "timezone": "America/Bogota",
            },
        ).json()

        employee_response = client.put(
            "/v1/workforce/employees/talent-employee-001",
            headers=internal_headers,
            json={
                "display_name": "Biometric Employee",
                "status": "active",
                "site_id": site["id"],
                "attendance_eligible": True,
            },
        )
        assert employee_response.status_code == 200
        employee = employee_response.json()
        employee_id = UUID(employee["id"])

        provision = client.post(
            "/v1/devices",
            headers=internal_headers,
            json={
                "site_id": site["id"],
                "name": "Reception Tablet 01",
            },
        ).json()

        enrollment_response = client.post(
            f"/v1/biometrics/employees/{employee_id}/enroll",
            headers=internal_headers,
            files={
                "image": ("employee.jpg", b"enrollment-face", "image/jpeg"),
            },
        )
        assert enrollment_response.status_code == 200
        assert enrollment_response.json()["face_count"] == 1
        assert provider.enroll_calls == 1

        kiosk_headers = {
            "X-Device-Id": provision["id"],
            "X-Device-Secret": provision["device_secret"],
            "Idempotency-Key": "android-request-0001",
        }

        first = client.post(
            "/v1/kiosk/recognize",
            headers=kiosk_headers,
            data={"event_type": "check_in"},
            files={"image": ("capture.jpg", b"kiosk-face", "image/jpeg")},
        )
        assert first.status_code == 200
        first_payload = first.json()
        assert first_payload["employee_id"] == str(employee_id)
        assert first_payload["similarity"] == 99.4
        assert first_payload["attendance"]["created"] is True
        assert first_payload["attendance"]["event_type"] == "check_in"
        assert provider.recognize_calls == 1

        retry = client.post(
            "/v1/kiosk/recognize",
            headers=kiosk_headers,
            data={"event_type": "check_in"},
            files={"image": ("capture.jpg", b"kiosk-face", "image/jpeg")},
        )
        assert retry.status_code == 200
        retry_payload = retry.json()
        assert retry_payload["attendance"]["created"] is False
        assert retry_payload["attendance"]["id"] == first_payload["attendance"]["id"]
        assert provider.recognize_calls == 1
    finally:
        app.dependency_overrides.clear()
