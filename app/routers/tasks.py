from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from app.models import User, Task, TaskStatus, Comment, Team
from app.core.config import templates

router = APIRouter()


@router.get("/my_tasks", response_class=HTMLResponse)
def tasks_page(
    request: Request, 
    user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    
    task_service = TaskService(db)
    
    if user.role.value == 'admin':
        tasks = db.query(Task).options(joinedload(Task.comments)).all()
    elif user.role.value == 'manager':
        if user.team_id:
            tasks = db.query(Task).options(joinedload(Task.comments)).filter(Task.team_id == user.team_id).all()
        else:
            tasks = []
    else:
        tasks = db.query(Task).options(joinedload(Task.comments)).filter(Task.assigned_to == user.id).all()
    for task in tasks:
        task.comments = sorted(task.comments, key=lambda c: c.created_at)
    
    members = []
    if user.team_id:
        members = db.query(User).filter(User.team_id == user.team_id).all()
    elif user.role.value == 'admin':
        members = db.query(User).all()
    
    statuses = db.query(TaskStatus).all()
    
    return templates.TemplateResponse(
        request, 
        "tasks.html", 
        {
            "tasks": tasks,
            "user": user, 
            "statuses": statuses,
            "team_members": members
        }
    )

@router.post("/create_task")
def create_task(
    title: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(None),
    assigned_to: int = Form(None),
    db: Session = Depends(get_db),
    user = Depends(require_manager)
):
    if isinstance(user, RedirectResponse):
        return user
    
    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            return HTMLResponse(
                "<h2>Неверный формат даты дедлайна</h2><a href='/my_tasks'>Назад</a>",
                status_code=400
            )
    
    team_id = user.team_id if user.role.value == 'manager' else None
    
    task_data = TaskCreate(
        title=title, 
        description=description, 
        deadline=deadline_dt, 
        assigned_to=assigned_to,
        team_id=team_id
    )
    task_service = TaskService(db)
    task = task_service.create_task(task_data, user)
    return RedirectResponse(url="/my_tasks", status_code=302)


@router.post("/update_task")
def update_task(
    task_id: int = Form(...),
    status_id: int = Form(None),
    title: str = Form(None),
    description: str = Form(None),
    deadline: str = Form(None),
    assigned_to: int = Form(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            return HTMLResponse(
                "<h2>Неверный формат даты дедлайна</h2><a href='/my_tasks'>Назад</a>",
                status_code=400
            )
    
    task_data = TaskUpdate(
        title=title,
        description=description,
        deadline=deadline_dt,
        status_id=status_id,
        assigned_to=assigned_to
    )
    task_service = TaskService(db)
    task_service.update_task(task_id, task_data, user)
    return RedirectResponse(url="/my_tasks", status_code=302)


@router.post("/delete_task")
def delete_task(
    task_id: int = Form(...),
    db: Session = Depends(get_db),
    user = Depends(require_manager)
):
    if isinstance(user, RedirectResponse):
        return user
    
    task_service = TaskService(db)
    task_service.delete_task(task_id, user)
    return RedirectResponse(url="/my_tasks", status_code=302)
