from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.models import Evaluation, Task, User
from app.core.config import settings
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.evaluation import EvaluationCreate


class EvaluationService:

    def __init__(self, db: Session):
        self.db = db

    def get_evaluations(self, user_id: int) -> List[Evaluation]:
        """Получить оценки пользователя"""
        return self.db.query(Evaluation).filter(Evaluation.user_id == user_id).all()

    def get_mean_score(self, user_id: int) -> float:
        """Получить средний балл пользователя"""
        avg_score = self.db.query(func.avg(Evaluation.score)).filter(
            Evaluation.user_id == user_id
        ).scalar()
        return round(avg_score, 1) if avg_score else 0.0

    def create_evaluation(self, eval_data: EvaluationCreate, evaluator: User) -> Evaluation:
        if not (0 <= eval_data.score <= settings.MAX_EVALUATION_SCORE):
            raise BadRequestException(
                f"Оценка должна быть от 0 до {settings.MAX_EVALUATION_SCORE}"
            )

        task = self.db.query(Task).filter(Task.id == eval_data.task_id).first()
        if not task:
            raise NotFoundException("Задача не найдена")
        if not task.assigned_to:
            raise NotFoundException("У задачи нет ответственного")

        evaluation = Evaluation(
            task_id=eval_data.task_id,
            user_id=task.assigned_to,
            score=eval_data.score
        )

        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        return evaluation
