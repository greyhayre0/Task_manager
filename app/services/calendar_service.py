from datetime import datetime, timedelta
from calendar import monthrange
from sqlalchemy.orm import Session
from app.models import Task, Meeting

def calendar_month(db: Session, user_id: int, year: int, month: int) -> dict:
    start = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day) + timedelta(days=1)

    tasks = db.query(Task).filter(
        Task.assigned_to == user_id,
        Task.deadline >= start,
        Task.deadline < end
    ).all()

    meetings = db.query(Meeting).filter(
        Meeting.user_id == user_id,
        Meeting.datetime >= start,
        Meeting.datetime < end
    ).all()

    return {
        "view": "month",
        "year": year,
        "month": month,
        "month_name": start.strftime("%B %Y"),
        "tasks": tasks,
        "meetings": meetings,
        "days_in_month": last_day,
    }

def calendar_day(db: Session, user_id: int, date_str: str) -> dict:
    selected_day = datetime.fromisoformat(date_str)
    next_day = selected_day + timedelta(days=1)

    tasks = db.query(Task).filter(
        Task.assigned_to == user_id,
        Task.deadline >= selected_day,
        Task.deadline < next_day
    ).all()

    meetings = db.query(Meeting).filter(
        Meeting.user_id == user_id,
        Meeting.datetime >= selected_day,
        Meeting.datetime < next_day
    ).all()

    all_meetings = db.query(Meeting).filter(
        Meeting.user_id == user_id
    ).order_by(Meeting.datetime.desc()).limit(10).all()

    return {
        "view": "day",
        "current_date": date_str,
        "selected_day": selected_day.strftime("%d.%m.%Y"),
        "tasks_for_day": tasks,
        "meetings_for_day": meetings,
        "all_meetings": all_meetings,
    }