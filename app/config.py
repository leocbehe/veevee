from typing import Set
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "veevee"
    development_environment: str = "prod"
    db_hostname: str
    db_password: str
    db_port: str
    db_name: str
    db_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    domains: Set[str] = set()

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8") # Corrected Line

settings = Settings()