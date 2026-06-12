from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.meeting import MeetingCreate
from app.services.meeting_service import MeetingService
from app.core.config import templates
from app.core.exceptions import BadRequestException, ConflictException

router = APIRouter()
 

@router.get("/my_meetings", response_class=HTMLResponse)
def meetings_page(
    request: Request, 
    user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    meeting_service = MeetingService(db)
    meetings = meeting_service.get_meetings(user.id)
    
    meetings_list = [{"id": m.id, "title": m.title, "datetime": m.datetime.isoformat()} for m in meetings]
    return templates.TemplateResponse(
        request, 
        "meetings.html", 
        {"meetings": meetings_list, "user": user, "now": datetime.now()}
    )


@router.post("/create_meeting")
def create_meeting(
    title: str = Form(...),
    datetime_str: str = Form(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    data = MeetingCreate(title=title, datetime_str=datetime_str)
    meeting_service = MeetingService(db)
    
    try:
        meeting_service.create_meeting(data, user)
    except ConflictException as e:
        return HTMLResponse(
            f"<h2>{e.detail}</h2><a href='/my_meetings'>Назад</a>", 
            status_code=409
        )
    except BadRequestException as e:
        return HTMLResponse(
            f"<h2>{e.detail}</h2><a href='/my_meetings'>Назад</a>", 
            status_code=400
        )
    
    return RedirectResponse(url="/my_meetings", status_code=302)


@router.post("/cancel_meeting")
def cancel_meeting(
    meeting_id: int = Form(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    meeting_service = MeetingService(db)
    meeting_service.cancel_meeting(meeting_id, user)
    return RedirectResponse(url="/my_meetings", status_code=302)
