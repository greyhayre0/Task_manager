from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ConflictException
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.meeting import MeetingCreate
from app.services.meeting_service import MeetingService

router = APIRouter()


@router.post("/create_meeting")
async def create_meeting(
    title: str = Form(...),
    datetime_str: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    data = MeetingCreate(title=title, datetime_str=datetime_str)
    meeting_service = MeetingService(db)
    try:
        meeting_service.create_meeting(data, user)
    except ConflictException as e:
        query_string = urlencode({"error": [e.detail]}, doseq=True)
        return RedirectResponse(url=f"/my_meetings?{query_string}", status_code=302)
    except BadRequestException as e:
        query_string = urlencode({"error": [e.detail]}, doseq=True)
        return RedirectResponse(url=f"/my_meetings?{query_string}", status_code=302)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании встречи")
    return RedirectResponse(url="/my_meetings", status_code=302)


@router.post("/cancel_meeting")
async def cancel_meeting(
    meeting_id: int = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    meeting_service = MeetingService(db)
    try:
        meeting_service.cancel_meeting(meeting_id, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при отмене встречи")
    return RedirectResponse(url="/my_meetings", status_code=302)
