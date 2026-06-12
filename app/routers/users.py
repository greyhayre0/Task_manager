from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.services.user_service import UserService
from app.services.evaluation_service import EvaluationService
from app.models import User, UserRole, Task, TaskStatus, Team
from app.core.config import templates

router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request, 
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    context = {"user": user}
    eval_service = EvaluationService(db)
    
    team_members = []
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        context["team_name"] = team.name if team else None
        
        team_members = db.query(User).filter(User.team_id == user.team_id).all()
        for member in team_members:
            member.average_score = eval_service.get_mean_score(member.id)
    else:
        context["team_name"] = None
    
    context["team_members"] = team_members
    context["task_statuses"] = db.query(TaskStatus).all()
    
    if user.role == UserRole.ADMIN:
        users = db.query(User).all()
        for u in users:
            u.average_score = eval_service.get_mean_score(u.id)
        
        context["users"] = users
        context["tasks"] = db.query(Task).all()
        context["teams"] = db.query(Team).all()
        context["show_admin_panel"] = True
        
    elif user.role == UserRole.MANAGER:
        if user.team_id:
            context["team_tasks"] = db.query(Task).filter(Task.team_id == user.team_id).all()
        else:
            context["team_tasks"] = []
        
        context["show_manager_panel"] = True
    
    return templates.TemplateResponse(request, "profile.html", context)


@router.post("/update_profile")
def update_profile(
    request: Request, 
    email: str = Form(...),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    if email != user.email:
        if db.query(User).filter(User.email == email).first():
            return RedirectResponse(url="/profile?error=Email уже используется", status_code=302)
    
    user.email = email
    db.commit()
    
    if password:
        if len(password) < 8:
            return RedirectResponse(url="/profile?error=Пароль должен быть минимум 8 символов", status_code=302)
        user.password = password
        db.commit()
    
    return RedirectResponse(url="/profile", status_code=302)


@router.post("/delete_account")
def delete_account(
    request: Request,
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    user_service = UserService(db)
    
    if user.role == UserRole.ADMIN:
        if user_service.get_admin_count() <= 1:
            return RedirectResponse(url="/profile?error=Нельзя удалить единственного администратора", status_code=302)
    
    user_service.delete_user(user.id)
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    return response


@router.post("/delete_user")
def delete_user(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    
    user_service = UserService(db)
    
    if user_id == current_user.id:
        return RedirectResponse(url="/profile?error=Нельзя удалить самого себя через эту форму. Используйте удаление аккаунта в профиле", status_code=302)
    
    user_to_delete = user_service.get_user_by_id(user_id)
    
    if user_to_delete.role == UserRole.ADMIN and user_service.get_admin_count() <= 1:
        return RedirectResponse(url="/profile?error=Нельзя удалить единственного администратора", status_code=302)
    
    user_service.delete_user(user_id)
    return RedirectResponse(url="/profile", status_code=302)