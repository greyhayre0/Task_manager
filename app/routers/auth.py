from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/register")
async def register(
    email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    try:
        user_data = UserCreate(email=email, password=password)
    except ValidationError as e:
        errors = e.errors()
        detail = errors[0]["msg"] if errors else "Ошибка валидации"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email уже занят"
        )

    try:
        user = User(email=user_data.email, password=user_data.password)
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя",
        )

    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(
        "user_id",
        str(user.id),
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.post("/login")
async def login(
    email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
        )

    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(
        "user_id",
        str(user.id),
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    return response
