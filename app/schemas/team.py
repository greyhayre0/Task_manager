from typing import Optional

from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    name: str
    invite_code: Optional[str] = None

class TeamJoin(BaseModel):
    code: str


class TeamResponse(TeamBase):
    id: int
    invite_code: str
    
    class Config:
        from_attributes = True
