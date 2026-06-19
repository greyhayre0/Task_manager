from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models import UserRole


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if len(v) > 128:
            raise ValueError("Пароль не должен превышать 128 символов")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
