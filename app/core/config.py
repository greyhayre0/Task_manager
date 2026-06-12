from pydantic_settings import BaseSettings
from fastapi.templating import Jinja2Templates
from functools import lru_cache


class Settings(BaseSettings):
    
    DATABASE_URL: str = "sqlite:///./app.db"
    
    SECRET_KEY: str = "super-puper-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    APP_NAME: str = "Task Manager"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123456"
    MIN_ADMIN_COUNT: int = 1
    
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    INVITE_CODE_LENGTH: int = 6
    MAX_EVALUATION_SCORE: int = 5

    MEETING_DURATION_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
templates = Jinja2Templates(directory="templates")
