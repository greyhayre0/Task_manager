from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.core.config import settings
from app.models import Meeting, User
from app.core.exceptions import BadRequestException, NotFoundException, ConflictException
from app.schemas.meeting import MeetingCreate

class MeetingService:
    def __init__(self, db: Session):
        self.db = db

    def get_meeting(self, meeting_id: int) -> Meeting:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise NotFoundException(f"Встреча с id {meeting_id} не найдена")
        return meeting

    def get_meetings(self, user_id: int) -> List[Meeting]:
        return self.db.query(Meeting).filter(Meeting.user_id == user_id).order_by(Meeting.datetime).all()

    def check_meeting(
        self,
        user_id: int,
        meeting_dt: datetime,
        duration_minutes: int,
        exclude_meeting_id: int = None
    ) -> bool:
        end_dt = meeting_dt + timedelta(minutes=duration_minutes)
        query = self.db.query(Meeting).filter(
            Meeting.user_id == user_id,
            Meeting.datetime < end_dt,
            func.datetime(Meeting.datetime, f'+{duration_minutes} minutes') > meeting_dt
        )
        if exclude_meeting_id:
            query = query.filter(Meeting.id != exclude_meeting_id)
        return query.first() is not None

    def create_meeting(self, meeting_data: MeetingCreate, user: User) -> Meeting:
        try:
            meeting_dt = datetime.fromisoformat(meeting_data.datetime_str)
        except ValueError:
            raise BadRequestException("Неверный формат даты и времени")

        if self.check_meeting(user.id, meeting_dt, settings.MEETING_DURATION_MINUTES):
            raise ConflictException("Время пересекается с другой встречей")
        if meeting_dt < datetime.now():
            raise BadRequestException("Время встречи не может быть в прошлом")

        meeting = Meeting(
            title=meeting_data.title,
            datetime=meeting_dt,
            user_id=user.id,
            team_id=user.team_id
        )
        self.db.add(meeting)
        try:
            self.db.commit()
            self.db.refresh(meeting)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при создании встречи")
        return meeting

    def cancel_meeting(self, meeting_id: int, user: User) -> None:
        meeting = self.get_meeting(meeting_id)
        if meeting.user_id != user.id:
            raise NotFoundException("Встреча не найдена")
        self.db.delete(meeting)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при отмене встречи")