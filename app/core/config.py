import os
from dotenv import load_dotenv

load_dotenv()
class Settings():
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY")
    PUBLIC_KEY: str = os.getenv("PUBLIC_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCES_TOKEN_EXPIRE_MINUTES", 60))
    ACCES_TOKEN_EXPIRE_DAY: int = int(os.getenv("ACCES_TOKEN_EXPIRE_DAY", 1440))
    ALGORITHM: str = os.getenv("ALGORITHM")


    SMTP_HOST : str = os.getenv("SMTP_HOST")
    SMTP_PORT: str = os.getenv("SMTP_PORT")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_MAIL_FROM: str = os.getenv("SMTP_MAIL_FROM")


settings = Settings()
