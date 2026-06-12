from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Enum as SQLEnum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import ClassVar
from app.database import Base
from sqlalchemy.orm import validates
import bcrypt

class UserRole(str, enum.Enum):
    REGULAR = "regular"
    MANAGER = "manager"
    ADMIN = "admin"


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.REGULAR, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'), nullable=True)
    
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="creator", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", foreign_keys="Evaluation.user_id", back_populates="user", cascade="all, delete-orphan")
    
    _average_score: ClassVar[float] = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @validates('password')
    def _validate_password(self, key, value):
        if value and not value.startswith('$2b$'):
            if len(value) < 8:
                raise ValueError("Пароль должен содержать минимум 8 символов")
            return self.hash_password(value)
        return value
    
    @property
    def average_score(self) -> float:
        return self._average_score if self._average_score is not None else 0.0
    
    @average_score.setter
    def average_score(self, value: float):
        self._average_score = value


class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String(6), unique=True, nullable=False)
    
    members = relationship("User", back_populates="team", foreign_keys="User.team_id")
    tasks = relationship("Task", back_populates="team")
    meetings = relationship("Meeting", back_populates="team")


class TaskStatus(Base):
    __tablename__ = 'task_statuses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    
    tasks = relationship("Task", back_populates="status_obj")


class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default='')
    deadline = Column(DateTime, nullable=True)
    status_id = Column(Integer, ForeignKey('task_statuses.id', ondelete='SET NULL'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'), nullable=True)
    
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
    team = relationship("Team", back_populates="tasks")
    status_obj = relationship("TaskStatus", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_task_assigned_to', 'assigned_to'),
        Index('idx_task_status_id', 'status_id'),
        Index('idx_task_deadline', 'deadline'),
    )


class Meeting(Base):
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'), nullable=True)

    creator = relationship("User", back_populates="meetings")
    team = relationship("Team", back_populates="meetings")

    __table_args__ = (
        Index('idx_meeting_datetime', 'datetime'),
        Index('idx_meeting_user_id', 'user_id'),
    )


class Evaluation(Base):
    __tablename__ = 'evaluations'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)

    task = relationship("Task", back_populates="evaluations")
    user = relationship("User", foreign_keys=[user_id], back_populates="evaluations")

    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 5', name='check_score_range'),
        Index('idx_evaluation_task_id', 'task_id'),
        Index('idx_evaluation_user_id', 'user_id'),
    )


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")

    __table_args__ = (
        Index('idx_comment_task_id', 'task_id'),
        Index('idx_comment_created_at', 'created_at'),
    )
