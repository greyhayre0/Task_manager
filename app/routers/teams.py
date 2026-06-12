from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException, ForbiddenException
from app.database import get_db
from app.dependencies import get_current_user, require_manager, require_admin
from app.schemas.team import TeamCreate, TeamJoin
from app.services.team_service import TeamService
from app.models import User, UserRole, Team
from app.core.config import templates

router = APIRouter()


@router.get("/team_members", response_class=HTMLResponse)
def team_page(
    request: Request, 
    user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    
    team_service = TeamService(db)
    
    team_name = None
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = team.name if team else None
        members = team_service.get_team_members(user.team_id)
    else:
        members = []
    
    members_list = [{"id": m.id, "email": m.email, "role": m.role.value} for m in members]
    return templates.TemplateResponse(
        request, 
        "team_members.html", 
        {
            "members": members_list, 
            "user": user,
            "team_name": team_name,
            "has_team": user.team_id is not None
        }
    )

@router.post("/join_team")
def join_team(
    code: str = Form(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    data = TeamJoin(code=code)
    team_service = TeamService(db)
    
    try:
        team = team_service.join_team(data, user)
    except NotFoundException:
        query_string = urlencode({"error": [f"Команда с кодом '{code}' не найдена"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    except Exception as e:
        query_string = urlencode({"error": [f"Ошибка: {str(e)}"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    return RedirectResponse(url="/profile", status_code=302)


@router.post("/create_team")
def create_team(
    name: str = Form(...),
    invite_code: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user = Depends(require_admin)
):
    if isinstance(user, RedirectResponse):
        return user
    
    data = TeamCreate(name=name, invite_code=invite_code)
    team_service = TeamService(db)
    
    try:
        team = team_service.create_team(data, user)
    except (ConflictException, BadRequestException, ForbiddenException) as e:
        query_string = urlencode({"error": [str(e.detail)]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    return RedirectResponse(url="/team_members", status_code=302)


@router.post("/add_user_team")
def add_user_team(
    user_email: str = Form(...),
    team_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    
    team_service = TeamService(db)
    
    try:
        team_service.add_user_team(user_email, team_id, current_user)
    except (NotFoundException, ForbiddenException) as e:
        query_string = urlencode({"error": [str(e.detail)]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    return RedirectResponse(url="/profile", status_code=302)


@router.post("/remove_user_team")
def remove_user_team(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    
    team_service = TeamService(db)
    
    try:
        team_service.remove_user_team(user_id, current_user)
    except (NotFoundException, ForbiddenException) as e:
        query_string = urlencode({"error": [str(e.detail)]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    return RedirectResponse(url="/profile", status_code=302)

@router.post("/assign_role")
def assign_role(
    user_id: int = Form(...),
    new_role: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Назначить роль"""
    if isinstance(current_user, RedirectResponse):
        return current_user
    
    try:
        role_enum = UserRole(new_role)
    except ValueError:
        query_string = urlencode({"error": ["Неверная роль"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        query_string = urlencode({"error": ["Пользователь не найден"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    
    user.role = role_enum
    db.commit()
    return RedirectResponse(url="/profile", status_code=302)
