from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.config import templates
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Task, TaskStatus, Team, User, UserRole
from app.services.calendar_service import calendar_day, calendar_month
from app.services.evaluation_service import EvaluationService
from app.services.meeting_service import MeetingService
from app.services.team_service import TeamService

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def auth_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if user_id:
        try:
            id_int = int(user_id)
            user = db.query(User).filter(User.id == id_int).first()
            if user:
                return templates.TemplateResponse(
                    request, "profile.html", {"user": user}
                )
        except (ValueError, TypeError):
            pass
    return templates.TemplateResponse(request, "auth.html")


# Грубо говоря мы теперь не считаем балл а просто его забираем из бд
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    context = {"user": user}

    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        context["team_name"] = team.name if team else None
        context["team_members"] = (
            db.query(User).filter(User.team_id == user.team_id).all()
        )
    else:
        context["team_name"] = None
        context["team_members"] = []

    context["task_statuses"] = db.query(TaskStatus).all()

    if user.role == UserRole.ADMIN:
        context["users"] = db.query(User).all()
        context["tasks"] = db.query(Task).all()
        context["teams"] = db.query(Team).all()
        context["show_admin_panel"] = True
    elif user.role == UserRole.MANAGER:
        if user.team_id:
            context["team_tasks"] = (
                db.query(Task).filter(Task.team_id == user.team_id).all()
            )
        else:
            context["team_tasks"] = []
        context["show_manager_panel"] = True

    return templates.TemplateResponse(request, "profile.html", context)


# Коменты теперь сортируются в бд через оредербай
@router.get("/my_tasks", response_class=HTMLResponse)
async def tasks_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role == UserRole.ADMIN:
        tasks = db.query(Task).all()
    elif user.role == UserRole.MANAGER:
        if user.team_id:
            tasks = db.query(Task).filter(Task.team_id == user.team_id).all()
        else:
            tasks = []
    else:
        tasks = db.query(Task).filter(Task.assigned_to == user.id).all()

    members = []
    if user.team_id:
        members = db.query(User).filter(User.team_id == user.team_id).all()
    elif user.role == UserRole.ADMIN:
        members = db.query(User).all()

    statuses = db.query(TaskStatus).all()

    return templates.TemplateResponse(
        request,
        "tasks.html",
        {"tasks": tasks, "user": user, "statuses": statuses, "team_members": members},
    )


@router.get("/my_meetings", response_class=HTMLResponse)
async def meetings_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    meeting_service = MeetingService(db)
    meetings = meeting_service.get_meetings(user.id)

    return templates.TemplateResponse(
        request,
        "meetings.html",
        {"meetings": meetings, "user": user, "now": datetime.now()},
    )


@router.get("/team_members", response_class=HTMLResponse)
async def team_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_service = TeamService(db)
    team_name = None
    if user.team_id:
        team = db.query(Team).filter(Team.id == user.team_id).first()
        team_name = team.name if team else None
        members = team_service.get_team_members(user.team_id)
    else:
        members = []

    return templates.TemplateResponse(
        request,
        "team_members.html",
        {
            "members": members,
            "user": user,
            "team_name": team_name,
            "has_team": user.team_id is not None,
        },
    )


@router.get("/calendar/month", response_class=HTMLResponse)
async def calendar_month_page(
    request: Request,
    user: User = Depends(get_current_user),
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db),
):
    if year is None or month is None:
        now = datetime.now()
        year, month = now.year, now.month
    context = calendar_month(db, user.id, year, month)
    context["request"] = request
    context["user"] = user
    return templates.TemplateResponse(request, "calendar.html", context)


@router.get("/calendar/day", response_class=HTMLResponse)
async def calendar_day_page(
    request: Request,
    user: User = Depends(get_current_user),
    date: str = None,
    db: Session = Depends(get_db),
):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    context = calendar_day(db, user.id, date)
    context["request"] = request
    context["user"] = user
    return templates.TemplateResponse(request, "calendar.html", context)


@router.get("/my_scores", response_class=HTMLResponse)
async def scores_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eval_service = EvaluationService(db)
    scores = eval_service.get_evaluations(user.id)
    avg = eval_service.get_mean_score(user.id)

    return templates.TemplateResponse(
        request, "evaluations.html", {"scores": scores, "average": avg, "user": user}
    )
