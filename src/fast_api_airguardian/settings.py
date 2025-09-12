from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    base_url: AnyHttpUrl # for URLs validation

    class Config:
        env_file = ".env"

settings = Settings()