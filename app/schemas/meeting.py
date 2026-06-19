from pydantic import BaseModel

class MeetingBase(BaseModel):
    title: str

class MeetingCreate(MeetingBase):
    datetime_str: str

class MeetingResponse(MeetingBase):
    id: int
    datetime: str
    user_id: int
    team_id: int = None

    class Config:
        from_attributes = True
