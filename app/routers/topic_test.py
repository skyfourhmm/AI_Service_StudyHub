from fastapi import APIRouter
from pydantic import BaseModel
from app.services.render_topic import render_test

router = APIRouter(prefix="/generate-test", tags=["Test by Topic"])

class TestRequest(BaseModel):
    topic: str
    num_questions: int = 10
    question_types: list = None
    exam_type: str = "TOEIC"
    score_range: str = None

@router.post("/")
async def generate_test(req: TestRequest):
    return await render_test(**req.dict())
