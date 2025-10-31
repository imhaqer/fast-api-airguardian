from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, ConfigDict
from typing import Literal

class Settings(BaseSettings):
    """base_url: AnyHttpUrl
    database_url: PostgresDsn
    redis_url: RedisDsn
    api_secret: str = "default-secret"
    postgres_db: str
    postgres_user: str
    postgres_password: str
    database_url_async: str
    database_url_sync: PostgresDsn"""
    
    # Only require the essential variables that actually exist
    database_url: str  # This is auto-provided by Railway
    redis_url: str     # This is auto-provided by Railway
    base_url: str = "https://drones-api.hive.fi/drones"
    api_secret: str
    
    # Remove all the postgres_* and database_url_* fields that don't exist
    
    model_config = ConfigDict(env_file=".env")  # modern way

settings = Settings()