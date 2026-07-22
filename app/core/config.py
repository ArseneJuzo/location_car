from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    PRIVATE_KEY: str
    PUBLIC_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ACCESS_TOKEN_EXPIRE_DAY: int = 30
    ALGORITHM: str = "RS256"

    FRONTEND_URL: str = "http://localhost:3000"

    SMTP_HOST : Optional[str] = None
    SMTP_PORT: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_MAIL_FROM: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore" #ignore les variables en trop dans le .env
    )


settings = Settings()
