from functools import lru_cache

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
    aws_region: str = "us-east-2"
    rekognition_collection_id: str = "talent-id-employees"


@lru_cache
def get_settings() -> Settings:
    return Settings()
