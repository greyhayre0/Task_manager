from fastapi import Request
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from wtforms.validators import Optional as WTFOptional, DataRequired, ValidationError
from datetime import datetime
from app.database import SessionLocal, engine
from app.models import User, Team, TaskStatus, Task, UserRole
from app.core.security import verify_password
from app.core.config import settings

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        db = SessionLocal()
        user = db.query(User).filter(User.email == username).first()
        db.close()
        if user and verify_password(password, user.password) and user.role == UserRole.ADMIN:
            request.session.update({"admin_user_id": user.id})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id, User.role == UserRole.ADMIN).first()
        db.close()
        return bool(user)

def validate_password(form, field):
    password = field.data
    if password and len(password) < 8:
        raise ValidationError("Пароль должен содержать минимум 8 символов")

def validate_invite_code(form, field):
    code = field.data
    if code and len(code) != 6:
        raise ValidationError("Инвайт код должен содержать ровно 6 символов")

def setup_admin(app):
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    admin = Admin(app, engine, authentication_backend=auth_backend)

    class UserAdmin(ModelView, model=User):
        column_list = [User.id, User.email, User.role, User.team]
        column_details_list = [User.id, User.email, User.role, User.team]
        column_searchable_list = [User.email]
        column_sortable_list = [User.id, User.email, User.role]
        form_columns = [User.email, User.password, User.role, User.team]
        form_args = {
            "email": {
                "label": "Email",
                "validators": [DataRequired(message="Email обязателен")]
            },
            "password": {
                "label": "Пароль (мин. 8 символов)",
                "validators": [WTFOptional(), validate_password]
            },
            "role": {"label": "Роль"},
            "team": {"label": "Команда"}
        }
        name, name_plural, icon = "Пользователь", "Пользователи", "fa-solid fa-user"

        async def on_model_change(self, data, model, is_created, request):
            password = data.get("password")
            if is_created and not password:
                raise ValueError("Пароль обязателен при создании пользователя!")
            return data

    class TeamAdmin(ModelView, model=Team):
        column_list = [Team.id, Team.name, Team.invite_code, Team.members]
        column_searchable_list = [Team.name, Team.invite_code]
        form_columns = [Team.name, Team.invite_code]
        form_args = {
            "name": {
                "label": "Название команды",
                "validators": [DataRequired(message="Название команды обязательно")]
            },
            "invite_code": {
                "label": "Инвайт код (6 символов)",
                "validators": [DataRequired(message="Инвайт код обязателен"), validate_invite_code]
            }
        }
        name, name_plural, icon = "Команда", "Команды", "fa-solid fa-users"

        async def on_model_change(self, data, model, is_created, request):
            if not data.get("name"):
                raise ValueError("Название команды не может быть пустым")
            if not data.get("invite_code"):
                raise ValueError("Инвайт код не может быть пустым")
            if len(data.get("invite_code")) != 6:
                raise ValueError("Инвайт код должен содержать ровно 6 символов")
            return data

    class TaskAdmin(ModelView, model=Task):
        column_list = [Task.id, Task.title, Task.status_obj, Task.deadline, Task.assignee, Task.team]
        column_details_list = [Task.id, Task.title, Task.description, Task.status_obj, Task.deadline, Task.creator, Task.assignee, Task.team]
        column_searchable_list = [Task.title]
        column_sortable_list = [Task.id, Task.deadline]
        form_columns = [Task.title, Task.description, Task.deadline, Task.team, Task.assignee, Task.status_obj]
        column_labels = {
            "status_obj": "Статус",
            "created_by": "Создатель",
            "assigned_to": "Исполнитель"
        }
        form_args = {
            "title": {
                "label": "Название задачи",
                "validators": [DataRequired(message="Название задачи обязательно")]
            },
            "description": {
                "label": "Описание задачи",
                "validators": [DataRequired(message="Описание задачи обязательно")]
            },
            "deadline": {
                "label": "Дедлайн",
                "validators": [DataRequired(message="Дедлайн обязателен")]
            },
            "team": {"label": "Команда"},
            "assignee": {"label": "Ответственный"},
            "status_obj": {"label": "Статус"}
        }
        name, name_plural, icon = "Задача", "Задачи", "fa-solid fa-list-check"

        async def on_model_change(self, data, model, is_created, request):
            if not data.get("title"):
                raise ValueError("Название задачи обязательно")
            if not data.get("description"):
                raise ValueError("Описание задачи обязательно")
            if not data.get("deadline"):
                raise ValueError("Дедлайн обязателен")
            if not data.get("team"):
                raise ValueError("Команда обязательна")
            if model.deadline and model.deadline < datetime.now():
                raise ValueError("Дедлайн не может быть в прошлом!")
            if is_created:
                db = SessionLocal()
                if not data.get("status_obj"):
                    default_status = db.query(TaskStatus).filter(TaskStatus.code == "open").first()
                    if default_status:
                        model.status_id = default_status.id
                admin_user_id = request.session.get("admin_user_id")
                if admin_user_id:
                    admin_user = db.query(User).filter(User.id == admin_user_id).first()
                    if admin_user:
                        model.creator = admin_user
                db.close()
            return data

    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
