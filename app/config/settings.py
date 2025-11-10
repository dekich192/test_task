from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost/auth_system"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
