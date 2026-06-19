import logging

import bcrypt

from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    if not hashed_password or not plain_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_session_cookie(user_id: int) -> dict:
    """Создаёт безопасные настройки для сессии"""
    return {
        "key": "user_id",
        "value": str(user_id),
        "httponly": True,
        "samesite": "lax",
        "max_age": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
