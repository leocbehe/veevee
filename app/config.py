from typing import Set
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

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
    hf_token: str
    default_hf_model: str
    inference_provider: str
    default_ollama_model: str
    inference_url: str
    app_dir: str = os.path.dirname(os.path.abspath(__file__))

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings() # type: ignore