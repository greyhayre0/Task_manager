from datetime import datetime
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.models import UserRole
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/create_task")
async def create_task(
    title: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(None),
    assigned_to: int = Form(None),
    db: Session = Depends(get_db),
    user=Depends(require_manager),
):
    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            query_string = urlencode(
                {"error": ["Неверный формат даты дедлайна"]}, doseq=True
            )
            return RedirectResponse(url=f"/my_tasks?{query_string}", status_code=302)

    team_id = user.team_id if user.role == UserRole.MANAGER else None
    task_data = TaskCreate(
        title=title,
        description=description,
        deadline=deadline_dt,
        assigned_to=assigned_to,
        team_id=team_id,
    )
    task_service = TaskService(db)
    try:
        task_service.create_task(task_data, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании задачи")
    return RedirectResponse(url="/my_tasks", status_code=302)


@router.post("/update_task")
async def update_task(
    task_id: int = Form(...),
    status_id: int = Form(None),
    title: str = Form(None),
    description: str = Form(None),
    deadline: str = Form(None),
    assigned_to: int = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            query_string = urlencode(
                {"error": ["Неверный формат даты дедлайна"]}, doseq=True
            )
            return RedirectResponse(url=f"/my_tasks?{query_string}", status_code=302)

    task_data = TaskUpdate(
        title=title,
        description=description,
        deadline=deadline_dt,
        status_id=status_id,
        assigned_to=assigned_to,
    )
    task_service = TaskService(db)
    try:
        task_service.update_task(task_id, task_data, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при обновлении задачи")
    return RedirectResponse(url="/my_tasks", status_code=302)


@router.post("/delete_task")
async def delete_task(
    task_id: int = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_manager),
):
    task_service = TaskService(db)
    try:
        task_service.delete_task(task_id, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении задачи")
    return RedirectResponse(url="/my_tasks", status_code=302)
