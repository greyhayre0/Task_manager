from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_manager
from app.schemas.evaluation import EvaluationCreate
from app.services.evaluation_service import EvaluationService
from app.core.config import templates

router = APIRouter()


@router.get("/my_scores", response_class=HTMLResponse)
def scores_page(
    request: Request, 
    user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if isinstance(user, RedirectResponse):
        return user
    
    eval_service = EvaluationService(db)
    scores = eval_service.get_evaluations(user.id)
    avg = eval_service.get_mean_score(user.id)
    
    data = {
        "scores": [{"task_id": s.task_id, "score": s.score} for s in scores], 
        "average": avg
    }
    return templates.TemplateResponse(
        request, 
        "evaluations.html", 
        {"scores": data, "user": user}
    )


@router.post("/evaluate_task")
def evaluate_task(
    task_id: int = Form(...),
    score: int = Form(...),
    db: Session = Depends(get_db),
    user = Depends(require_manager)
):
    if isinstance(user, RedirectResponse):
        return user
    
    data = EvaluationCreate(task_id=task_id, score=score)
    eval_service = EvaluationService(db)
    eval_service.create_evaluation(data, user)
    return RedirectResponse(url="/my_tasks", status_code=302)
