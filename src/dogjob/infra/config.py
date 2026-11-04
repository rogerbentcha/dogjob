from functools import lru_cache

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration lue depuis l'environnement (préfixe DOGJOB_) ou un fichier .env local."""

    model_config = SettingsConfigDict(env_prefix="DOGJOB_", env_file=".env", extra="ignore")

    # Secrets : aucune valeur par défaut, ils doivent venir de l'environnement.
    api_key: SecretStr
    database_url: SecretStr
    resend_api_key: SecretStr
    reminder_recipient: EmailStr

    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
