from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TALENT_ID_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "Talent ID API"
    environment: str = "local"
    expose_docs: bool = True

    database_url: str = (
        "postgresql+psycopg://talent_id:talent_id_local@localhost:5432/talent_id"
    )
    internal_api_key: SecretStr | None = None
    aws_region: str = "us-east-2"
    rekognition_collection_id: str = "talent-id-employees"
    rekognition_match_threshold: float = Field(default=98.0, ge=0, le=100)
    rekognition_association_threshold: float = Field(default=90.0, ge=0, le=100)


@lru_cache
def get_settings() -> Settings:
    return Settings()
