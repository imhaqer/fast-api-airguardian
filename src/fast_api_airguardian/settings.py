from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn
from typing import Literal

class Settings(BaseSettings):
    base_url: AnyHttpUrl # for URLs validation
    database_url: PostgresDsn
    redis_url: RedisDsn

    class Config:
        env_file = ".env"

settings = Settings()