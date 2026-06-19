from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_manager
from app.schemas.evaluation import EvaluationCreate
from app.services.evaluation_service import EvaluationService

router = APIRouter()

@router.post("/evaluate_task")
async def evaluate_task(
    task_id: int = Form(...),
    score: int = Form(...),
    db: Session = Depends(get_db),
    user = Depends(require_manager)
):
    data = EvaluationCreate(task_id=task_id, score=score)
    eval_service = EvaluationService(db)
    try:
        eval_service.create_evaluation(data, user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении оценки")
    return RedirectResponse(url="/my_tasks", status_code=302)
