from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models import Task, TaskStatus, User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def get_task_by_id(self, task_id: int) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise NotFoundException(f"Задача с id {task_id} не найдена")
        return task

    def get_user_tasks(self, user_id: int) -> List[Task]:
        return self.db.query(Task).filter(Task.assigned_to == user_id).all()

    def get_default_status(self) -> Optional[TaskStatus]:
        return self.db.query(TaskStatus).filter(TaskStatus.code == "open").first()

    def create_task(self, task_data: TaskCreate, creator: User) -> Task:
        if creator.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise ForbiddenException("Только руководитель может создавать задачи")
        if task_data.deadline and task_data.deadline < datetime.now():
            raise BadRequestException("Дедлайн не может быть в прошлом")

        default_status = self.get_default_status()
        team_id = None
        if task_data.assigned_to:
            assignee = (
                self.db.query(User).filter(User.id == task_data.assigned_to).first()
            )
            if assignee:
                team_id = assignee.team_id
        else:
            team_id = creator.team_id

        task = Task(
            title=task_data.title,
            description=task_data.description or "",
            deadline=task_data.deadline,
            created_by=creator.id,
            assigned_to=task_data.assigned_to,
            team_id=team_id,
            status_id=default_status.id if default_status else None,
        )
        self.db.add(task)
        try:
            self.db.commit()
            self.db.refresh(task)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при создании задачи")
        return task

    def update_task(self, task_id: int, task_data: TaskUpdate, user: User) -> Task:
        task = self.get_task_by_id(task_id)
        is_manager = user.role in [UserRole.ADMIN, UserRole.MANAGER]
        is_assignee = task.assigned_to == user.id
        is_creator = task.created_by == user.id

        if not (is_manager or is_assignee or is_creator):
            raise ForbiddenException("Нет прав на изменение задачи")
        if task_data.deadline and task_data.deadline < datetime.now():
            raise BadRequestException("Дедлайн не может быть в прошлом")

        if not is_manager and not is_creator:
            if any(
                [
                    task_data.title is not None,
                    task_data.description is not None,
                    task_data.deadline is not None,
                    task_data.assigned_to is not None,
                ]
            ):
                raise ForbiddenException(
                    "Исполнитель может менять только статус задачи"
                )

        if task_data.title is not None and (is_manager or is_creator):
            task.title = task_data.title
        if task_data.description is not None and (is_manager or is_creator):
            task.description = task_data.description
        if task_data.deadline is not None and (is_manager or is_creator):
            task.deadline = task_data.deadline
        if task_data.assigned_to is not None and (is_manager or is_creator):
            assignee = (
                self.db.query(User).filter(User.id == task_data.assigned_to).first()
            )
            if assignee:
                task.assigned_to = task_data.assigned_to
                if assignee.team_id:
                    task.team_id = assignee.team_id
        if task_data.status_id is not None:
            task.status_id = task_data.status_id

        try:
            self.db.commit()
            self.db.refresh(task)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при обновлении задачи")
        return task

    def delete_task(self, task_id: int, user: User) -> None:
        task = self.get_task_by_id(task_id)
        is_manager = user.role in [UserRole.ADMIN, UserRole.MANAGER]
        is_creator = task.created_by == user.id
        if not (is_manager or is_creator):
            raise ForbiddenException("Нет прав на удаление задачи")
        self.db.delete(task)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при удалении задачи")
