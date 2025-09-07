from typing import List

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Billing System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI-based billing system with PostgreSQL"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    # Email Configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool

    # Denominations
    DEFAULT_DENOMINATIONS: List[int] = [500, 200, 100, 50, 20, 10, 5, 2, 1]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
