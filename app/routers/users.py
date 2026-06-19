from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.services.user_service import UserService
from app.models import User, UserRole

router = APIRouter()

@router.post("/update_profile")
async def update_profile(
    email: str = Form(...),
    password: str = Form(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if email != user.email:
        if db.query(User).filter(User.email == email).first():
            query_string = urlencode({"error": ["Email уже используется"]}, doseq=True)
            return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    if password and len(password) < 8:
        query_string = urlencode({"error": ["Пароль должен быть минимум 8 символов"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)

    user.email = email
    if password:
        user.password = password

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при обновлении профиля")
    
    return RedirectResponse(url="/profile", status_code=302)

@router.post("/delete_account")
async def delete_account(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    user_service = UserService(db)
    if user.role == UserRole.ADMIN:
        if user_service.get_admin_count() <= 1:
            query_string = urlencode({"error": ["Нельзя удалить единственного администратора"]}, doseq=True)
            return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    try:
        user_service.delete_user(user.id)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении аккаунта")
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    return response

@router.post("/delete_user")
async def delete_user(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    if user_id == current_user.id:
        query_string = urlencode({"error": ["Нельзя удалить самого себя тут"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)

    user_service = UserService(db)
    user_to_delete = user_service.get_user_by_id(user_id)
    if user_to_delete.role == UserRole.ADMIN and user_service.get_admin_count() <= 1:
        query_string = urlencode({"error": ["Нельзя удалить единственного администратора"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)

    try:
        user_service.delete_user(user_id)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя")
    return RedirectResponse(url="/profile", status_code=302)
