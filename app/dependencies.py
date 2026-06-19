from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException
from app.database import get_db
from app.models import User, UserRole


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован"
        )
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный id пользователя"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )
    return user


def require_admin(user: User = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise ForbiddenException("Требуется роль админа")
    return user


def require_manager(user: User = Depends(get_current_user)):
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise ForbiddenException("Требуется роль менеджера или админа")
    return user


def require_auth(user: User = Depends(get_current_user)):
    return user
