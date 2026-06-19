from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""


class TaskCreate(TaskBase):
    deadline: Optional[datetime] = None
    assigned_to: Optional[int] = None
    team_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    status_id: Optional[int] = None
    deadline: Optional[datetime] = None
    created_by: int
    assigned_to: Optional[int] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
