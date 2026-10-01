from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from talent_id.shared.auth import require_internal_key
from talent_id.shared.config import Settings, get_settings


def build_client(configured_key: str | None) -> TestClient:
    app = FastAPI()

    def override_settings() -> Settings:
        return Settings(
            internal_api_key=SecretStr(configured_key) if configured_key else None,
        )

    app.dependency_overrides[get_settings] = override_settings

    @app.get("/private", dependencies=[Depends(require_internal_key)])
    def private_endpoint() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_internal_key_is_required() -> None:
    client = build_client("secret")

    assert client.get("/private").status_code == 422
    assert client.get("/private", headers={"X-Internal-Key": "wrong"}).status_code == 401
    assert client.get("/private", headers={"X-Internal-Key": "secret"}).status_code == 200


def test_internal_api_fails_closed_when_not_configured() -> None:
    client = build_client(None)

    response = client.get("/private", headers={"X-Internal-Key": "anything"})
    assert response.status_code == 503
