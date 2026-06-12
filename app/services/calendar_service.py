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
    
    calendar = {day: {"tasks": [], "meetings": []} for day in range(1, last_day + 1)}
    
    for task in tasks:
        if task.deadline:
            calendar[task.deadline.day]["tasks"].append(task.title)
            
    for meeting in meetings:
        if meeting.datetime:
            calendar[meeting.datetime.day]["meetings"].append(meeting.title)
    
    return {
        "view": "month",
        "year": year,
        "month": month,
        "month_name": start.strftime("%B %Y"),
        "calendar_data": calendar,
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
        "tasks_for_day": [{"title": t.title, "deadline": t.deadline.strftime("%H:%M") if t.deadline else ""} for t in tasks],
        "meetings_for_day": [{"title": m.title, "datetime": m.datetime.strftime("%H:%M") if m.datetime else ""} for m in meetings],
        "all_meetings": [{"title": m.title, "datetime": m.datetime} for m in all_meetings],
    }
