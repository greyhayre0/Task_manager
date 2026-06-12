import random
import string
from sqlalchemy.orm import Session
from typing import List

from app.models import Team, User, UserRole
from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException, ConflictException
from app.schemas.team import TeamCreate, TeamJoin
 

class TeamService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_team_by_id(self, team_id: int) -> Team:
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise NotFoundException(f"Команда с ID {team_id} не найдена")
        return team
    
    def get_team_by_invite_code(self, invite_code: str) -> Team:
        team = self.db.query(Team).filter(Team.invite_code == invite_code.upper()).first()
        if not team:
            raise NotFoundException("Команда с таким кодом не найдена")
        return team
    
    def get_team_members(self, team_id: int) -> List[User]:
        return self.db.query(User).filter(User.team_id == team_id).all()
    
    def generate_invite_code(self) -> str:
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=settings.INVITE_CODE_LENGTH
            ))
            if not self.db.query(Team).filter(Team.invite_code == code).first():
                return code
    
    def create_team(self, team_data: TeamCreate, creator: User) -> Team:
        if creator.role != UserRole.ADMIN:
            raise ForbiddenException("Только администратор может создавать команды")
        
        if team_data.invite_code:
            invite_code = team_data.invite_code.upper()
            existing = self.db.query(Team).filter(Team.invite_code == invite_code).first()
            if existing:
                raise ConflictException("Команда с таким инвайт кодом уже существует")
            if len(invite_code) != settings.INVITE_CODE_LENGTH:
                raise BadRequestException("Инвайт код должен содержать ровно 6 символов")
        else:
            invite_code = self.generate_invite_code()
        
        team = Team(
            name=team_data.name,
            invite_code=invite_code
        )
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        return team
    
    def join_team(self, team_data: TeamJoin, user: User) -> Team:
        team = self.get_team_by_invite_code(team_data.code)
        user.team_id = team.id
        self.db.commit()
        return team
    
    def add_user_team(self, user_email: str, team_id: int, current_user: User) -> User:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise ForbiddenException("Недостаточно прав")
        
        user = self.db.query(User).filter(User.email == user_email).first()
        if not user:
            raise NotFoundException("Пользователь не найден")
        
        user.team_id = team_id
        self.db.commit()
        return user
    
    def remove_user_team(self, user_id: int, current_user: User) -> None:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise ForbiddenException("Недостаточно прав")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.team_id = None
            self.db.commit()
