from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn
from typing import Literal

class Settings(BaseSettings):
    base_url: AnyHttpUrl # for URLs validation
    database_url: PostgresDsn
    redis_url: RedisDsn
    api_secret: str = "default-secret"
    postgres_user: str
    postgres_password: str
    database_url_async: str  # async URL (with asyncpg)
    database_url_sync: PostgresDsn   # sync URL (without asyncpg)
    postgres_db: str
    
    class Config:
        env_file = ".env"

settings = Settings()