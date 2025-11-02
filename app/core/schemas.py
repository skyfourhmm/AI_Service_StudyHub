from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import date


# thêm progresss trend và speed vào personalized plan

class ProgressTrend(BaseModel):
    past_tests: int
    accuracy_growth_rate: float
    strong_skills: List[str]
    weak_skills: List[str]
    consistency_index: float


class ProgressSpeed(BaseModel):
    category: str
    description: str
    trend: ProgressTrend
    predicted_reach_next_level_weeks: int
    recommendation: str


class WeeklyGoal(BaseModel):
    week: int
    topic: str
    description: str
    study_methods: List[str]
    materials: List[str]
    hours: int


class PersonalizedPlan(BaseModel):
    progress_speed: ProgressSpeed
    weekly_goals: List[WeeklyGoal]
# end thêm

class QuestionKey(BaseModel):
    id: int
    question: Optional[str] = None 
    answer: str
    skill: Optional[str] = None
    topic: Optional[str] = None


class TestInfo(BaseModel):
    title: Optional[str] = None
    total_questions: Optional[int] = None


class PerQuestionResult(BaseModel):
    id: int
    question: Optional[str] = None 
    correct: bool
    expected_answer: str
    user_answer: Optional[str] = None
    skill: Optional[str] = None
    topic: Optional[str] = None
    explain: Optional[str] = None


class SkillSummary(BaseModel):
    skill: str
    total: int
    correct: int
    accuracy: float


class GradeResponse(BaseModel):
    total_score: int
    total_questions: int
    per_question: List[PerQuestionResult]
    skill_summary: List[SkillSummary]
    weak_topics: List[str]
    recommendations: Optional[List[str]] = None
    personalized_plan: Optional[PersonalizedPlan] = None  # 
    current_level: str 
    post_test_level: str


class TestHistoryItem(BaseModel):
    test_date: date
    level_at_test: str
    per_question: List[PerQuestionResult] = []
    weak_topics: List[str] = []

class LearningProfile(BaseModel):
    student_id: str
    name: str
    current_level: str
    study_hours_per_week: int
    learning_goals: str
    learning_preferences: List[str]
    study_methods: List[str]
    test_history: List[TestHistoryItem]


class GradeRequest(BaseModel):
    test_info: Optional[TestInfo] = None
    answer_key: List[QuestionKey]
    student_answers: Dict[str, str]
    use_gemini: Optional[bool] = False
    profile: Optional[LearningProfile]

