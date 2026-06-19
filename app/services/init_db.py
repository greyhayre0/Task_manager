from sqlalchemy.orm import Session
from app.models import User, TaskStatus, UserRole
from app.core.config import settings

def init_db(db: Session):
    if not db.query(User).filter(User.email == settings.ADMIN_EMAIL).first():
        admin = User(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            role=UserRole.ADMIN
        )
        db.add(admin)

    default_statuses = [
        {"name": "Открыто", "code": "open"},
        {"name": "В работе", "code": "in_progress"},
        {"name": "Завершено", "code": "done"}
    ]
    for status_data in default_statuses:
        if not db.query(TaskStatus).filter(TaskStatus.code == status_data["code"]).first():
            db.add(TaskStatus(**status_data))
    db.commit()
