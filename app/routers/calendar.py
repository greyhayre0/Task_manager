from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.core.config import templates
from app.services.calendar_service import calendar_month, calendar_day

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/month", response_class=HTMLResponse)
def calendar_month_page(
    request: Request,
    user: User = Depends(get_current_user),
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
    ):
    if isinstance(user, RedirectResponse):
        return user

    if year is None or month is None:
        now = datetime.now()
        year, month = now.year, now.month

    context = calendar_month(db, user.id, year, month)
    context["request"] = request
    context["user"] = user
    return templates.TemplateResponse(request, "calendar.html", context)


@router.get("/day", response_class=HTMLResponse)
def calendar_day_page(
    request: Request,
    user: User = Depends(get_current_user),
    date: str = datetime.now().strftime("%Y-%m-%d"),
    db: Session = Depends(get_db)
    ):
    if isinstance(user, RedirectResponse):
        return user

    context = calendar_day(db, user.id, date)
    context["request"] = request
    context["user"] = user
    return templates.TemplateResponse(request, "calendar.html", context)
