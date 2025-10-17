from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, ConfigDict
from typing import Literal

class Settings(BaseSettings):
    base_url: AnyHttpUrl
    database_url: PostgresDsn
    redis_url: RedisDsn
    api_secret: str = "default-secret"
    postgres_db: str
    postgres_user: str
    postgres_password: str
    database_url_async: str
    database_url_sync: PostgresDsn
    
    model_config = ConfigDict(env_file=".env")  # modern way

settings = Settings()