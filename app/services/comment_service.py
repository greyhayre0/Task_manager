from sqlalchemy.orm import Session
from typing import List

from app.models import Comment, User
from app.schemas.comment import CommentCreate


class CommentService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_comments(self, task_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(
            Comment.task_id == task_id
        ).order_by(Comment.created_at).all()
    
    def create_comment(self, comment_data: CommentCreate, user: User) -> Comment:
        comment = Comment(
            task_id=comment_data.task_id,
            user_id=user.id,
            text=comment_data.text
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
