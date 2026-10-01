import hmac

from fastapi import Depends, Header, HTTPException, status

from talent_id.shared.config import Settings, get_settings


def require_internal_key(
    x_internal_key: str = Header(alias="X-Internal-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    configured = settings.internal_api_key
    if configured is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="internal API authentication is not configured",
        )

    if not hmac.compare_digest(x_internal_key, configured.get_secret_value()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid internal API credentials",
        )
