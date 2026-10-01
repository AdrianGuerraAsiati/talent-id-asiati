from fastapi import FastAPI

from talent_id import __version__
from talent_id.modules.devices.api import kiosk_router, router as devices_router
from talent_id.modules.workforce.api import router as workforce_router
from talent_id.shared.config import get_settings


def build_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url="/docs" if settings.expose_docs else None,
        redoc_url=None,
    )

    app.include_router(workforce_router)
    app.include_router(devices_router)
    app.include_router(kiosk_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "talent-id-api",
            "version": __version__,
            "environment": settings.environment,
        }

    return app
