from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment_service import CommentService

router = APIRouter()


@router.post("/add_comment")
async def add_comment(
    task_id: int = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    data = CommentCreate(task_id=task_id, text=text)
    comment_service = CommentService(db)
    try:
        comment_service.create_comment(data, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при добавлении комментария")
    return RedirectResponse(url="/my_tasks", status_code=302)


@router.get("/task_comments/{task_id}", response_model=list[CommentResponse])
async def task_comments(
    task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    comment_service = CommentService(db)
    return comment_service.get_comments(task_id)
