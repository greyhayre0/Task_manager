from sqlalchemy.orm import Session
from app.models import User, UserRole
from app.core.security import verify_password
from app.core.exceptions import NotFoundException, ConflictException
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"Пользователь с ID {user_id} не найден")
        return user
    
    def get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise NotFoundException(f"Пользователь с email {email} не найден")
        return user
    
    def check_email_exists(self, email: str, exclude_user_id: int = None) -> bool:
        """Проверить существует ли email"""
        query = self.db.query(User).filter(User.email == email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None
    
    def create_user(self, user_data: UserCreate, role: UserRole = UserRole.REGULAR) -> User:
        email = user_data.email.strip().lower()
        
        if self.check_email_exists(email):
            raise ConflictException(f"Email {email} уже зарегистрирован")
        
        user = User(
            email=email,
            password=user_data.password,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        
        if user_data.email:
            email = user_data.email.strip().lower()
            if self.check_email_exists(email, exclude_user_id=user_id):
                raise ConflictException(f"Email {email} уже занят")
            user.email = email
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
    
    def authenticate_user(self, email: str, password: str) -> User:
        email = email.strip().lower()
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password):
            raise NotFoundException("Неверный email или пароль")
        
        return user
    
    def get_admin_count(self) -> int:
        return self.db.query(User).filter(User.role == UserRole.ADMIN).count()
