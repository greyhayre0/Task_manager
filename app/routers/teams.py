from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from app.database import get_db
from app.dependencies import get_current_user, require_manager, require_admin
from app.schemas.team import TeamCreate, TeamJoin
from app.services.team_service import TeamService
from app.models import User, UserRole
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException, ForbiddenException

router = APIRouter()

@router.post("/join_team")
async def join_team(
    code: str = Form(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    data = TeamJoin(code=code)
    team_service = TeamService(db)
    try:
        team = team_service.join_team(data, user)
    except NotFoundException:
        query_string = urlencode({"error": [f"Команда с кодом '{code}' не найдена"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при присоединении к команде")
    return RedirectResponse(url="/profile", status_code=302)

@router.post("/create_team")
async def create_team(
    name: str = Form(...),
    invite_code: str = Form(None),
    db: Session = Depends(get_db),
    user = Depends(require_admin)
):
    data = TeamCreate(name=name, invite_code=invite_code)
    team_service = TeamService(db)
    try:
        team = team_service.create_team(data, user)
    except (ConflictException, BadRequestException, ForbiddenException) as e:
        query_string = urlencode({"error": [str(e.detail)]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании команды")
    return RedirectResponse(url="/team_members", status_code=302)

@router.post("/add_user_team")
async def add_user_team(
    user_email: str = Form(...),
    team_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    team_service = TeamService(db)
    try:
        team_service.add_user_team(user_email, team_id, current_user)
    except (NotFoundException, ForbiddenException) as e:
        query_string = urlencode({"error": [str(e.detail)]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при добавлении пользователя в команду")
    return RedirectResponse(url="/profile", status_code=302)

@router.post("/remove_user_team")
async def remove_user_team(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    team_service = TeamService(db)
    try:
        team_service.remove_user_team(user_id, current_user)
    except (NotFoundException, ForbiddenException) as e:
        query_string = urlencode({"error": [str(e.detail)]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя из команды")
    return RedirectResponse(url="/profile", status_code=302)

@router.post("/assign_role")
async def assign_role(
    user_id: int = Form(...),
    new_role: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    try:
        role_enum = UserRole(new_role)
    except ValueError:
        query_string = urlencode({"error": ["Неверная роль"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        query_string = urlencode({"error": ["Пользователь не найден"]}, doseq=True)
        return RedirectResponse(url=f"/profile?{query_string}", status_code=302)

    try:
        user.role = role_enum
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при назначении роли")
    return RedirectResponse(url="/profile", status_code=302)
