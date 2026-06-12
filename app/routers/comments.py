from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.comment import CommentCreate
from app.services.comment_service import CommentService

router = APIRouter()


@router.post("/add_comment")
def add_comment(
    task_id: int = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    data = CommentCreate(task_id=task_id, text=text)
    comment_service = CommentService(db)
    comment_service.create_comment(data, user)
    return RedirectResponse(url="/my_tasks", status_code=302)


@router.get("/task_comments/{task_id}")
def task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    comment_service = CommentService(db)
    comments = comment_service.get_comments(task_id)
    result = []
    for c in comments:
        item = {
            "user_id": c.user_id,
            "text": c.text,
            "created": c.created_at.isoformat()
            }
        result.append(item)
    return result
