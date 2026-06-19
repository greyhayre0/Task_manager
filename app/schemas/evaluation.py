from pydantic import BaseModel


class EvaluationBase(BaseModel):
    score: int


class EvaluationCreate(EvaluationBase):
    task_id: int


class EvaluationResponse(EvaluationBase):
    id: int
    task_id: int
    user_id: int

    class Config:
        from_attributes = True
