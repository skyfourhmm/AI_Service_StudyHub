from fastapi import APIRouter
from pydantic import BaseModel
from app.services.render_custom import render_test

router = APIRouter(prefix="/generate-test-custom", tags=["Custom Test"])

class CustomRequest(BaseModel):
    current_level: str
    toeic_score: int | None = None
    weak_skills: list[str] | None = None
    exam_type: str = "TOEIC"
    topics: list[str] | None = None
    difficulty: str | None = None
    question_ratio: str = "MCQ"
    num_questions: int = 15
    time_limit: int | None = 20

@router.post("/")
async def generate_custom(req: CustomRequest):
    return await render_test(**req.dict())
