from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MeetingBase(BaseModel):
    title: str


class MeetingCreate(MeetingBase):
    datetime_str: str


class MeetingResponse(MeetingBase):
    id: int
    datetime: datetime
    user_id: int
    team_id: Optional[int] = None
    
    class Config:
        from_attributes = True
