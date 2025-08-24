import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/practice"
    database_url_test: str = "postgresql://postgres:postgres@localhost:5432/practice"
    
    # AI Services
    openai_api_key: Optional[str] = None
    
    # Application
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"


settings = Settings()