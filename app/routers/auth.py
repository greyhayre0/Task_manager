from urllib.parse import urlencode
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.core.security import create_session_cookie, verify_password
from app.core.exceptions import ConflictException
from app.core.config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def auth_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if user_id:
        try:
            id_int = int(user_id)
            user = db.query(User).filter(User.id == id_int).first()
            if user:
                return RedirectResponse(url="/profile", status_code=302)
        except (ValueError, TypeError):
            pass
    
    return templates.TemplateResponse(request, "auth.html")


@router.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Самая простая проверка
    if len(password) < 8:
        return RedirectResponse(url="/?error=Пароль минимум 8 символов", status_code=302)
    
    # Проверка на существующий email
    if db.query(User).filter(User.email == email).first():
        return RedirectResponse(url="/?error=Email уже занят", status_code=302)
    
    # Создание пользователя (хэш сработает в модели)
    user = User(email=email, password=password)
    db.add(user)
    db.commit()
    
    # Установка cookie и редирект
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie("user_id", str(user.id), httponly=True)
    return response


@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Прямой запрос (без сервиса)
    user = db.query(User).filter(User.email == email).first()
    
    # Простая проверка
    if not user or not verify_password(password, user.password):
        return RedirectResponse(url="/?error=Неверный email или пароль", status_code=302)
    
    # Установка cookie
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie("user_id", str(user.id), httponly=True, max_age=86400)
    return response


@router.get("/logout", response_class=RedirectResponse)
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    return response
