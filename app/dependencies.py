from fastapi import Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from typing import Union

from app.database import get_db
from app.models import User, UserRole
from app.core.exceptions import ForbiddenException


def get_current_user(
    request: Request, 
    db: Session = Depends(get_db)
) -> Union[User, RedirectResponse]:
    """Получить текущего авторизованного пользователя или редирект"""
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=302)
    
    try:
        user_id = int(user_id)
    except ValueError:
        return RedirectResponse(url="/", status_code=302)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/", status_code=302)
    
    return user


def require_admin(user: Union[User, RedirectResponse] = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    if user.role != UserRole.ADMIN:
        raise ForbiddenException("Требуется роль админа")
    return user


def require_manager(user: Union[User, RedirectResponse] = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise ForbiddenException("Требуется роль менеджера или админа")
    return user


def require_auth(user: Union[User, RedirectResponse] = Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    return user

