from fastapi import APIRouter, HTTPException
from app.core.schemas import GradeRequest, GradeResponse
from app.core.grader import grade_locally
from app.core.gemini_client import call_gemini_analysis
from app.core.material_mapper import get_materials_from_database
from app.core.schemas import PerQuestionResult, SkillSummary, PersonalizedPlan
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/grade", tags=["Grading"])

@router.post("/", response_model=GradeResponse)
async def grade_endpoint(req: GradeRequest):
    try:
        total_correct, total_qs, per_q, skill_summary, weak_topics = grade_locally(
            req.answer_key, req.student_answers
        )

        recommendations = None
        personalized_plan = None

        def serialize_profile(profile):
            if not profile:
                return {}
            profile_dict = jsonable_encoder(profile)
            for item in profile_dict.get("test_history", []):
                item.pop("score", None)
                item.pop("notes", None)
            return profile_dict

        gemini_resp = {}
        if req.use_gemini:
            payload = {
                "test_info": req.test_info.dict() if req.test_info else {},
                "answer_key": [q.dict() for q in req.answer_key],
                "student_answers": req.student_answers,
                "profile": serialize_profile(req.profile)
            }

            gemini_resp = await call_gemini_analysis(payload)

            if "per_question" in gemini_resp:
                per_q = [PerQuestionResult(**p) for p in gemini_resp["per_question"]]
            if "skill_summary" in gemini_resp:
                skill_summary = [SkillSummary(**s) for s in gemini_resp["skill_summary"]]
            if "weak_topics" in gemini_resp:
                weak_topics = gemini_resp["weak_topics"]

            recommendations = gemini_resp.get("recommendations")
            personalized_plan_data = gemini_resp.get("personalized_plan")
            personalized_plan = None
            if personalized_plan_data:
                try:
                    personalized_plan = PersonalizedPlan(**personalized_plan_data)
                except Exception:
                    personalized_plan = personalized_plan_data

            if personalized_plan:
                if isinstance(personalized_plan, dict) and "weekly_goals" in personalized_plan:
                    for goal in personalized_plan["weekly_goals"]:
                        skill_detected = "Grammar"
                        for s in skill_summary:
                            if s.skill in goal.get("topic", ""):
                                skill_detected = s.skill
                                break
                        goal["materials"] = get_materials_from_database(skill_detected, weak_topics)
                else:
                    main_skill = skill_summary[0].skill if skill_summary else "Grammar"
                    materials = get_materials_from_database(main_skill, weak_topics)
                    if hasattr(personalized_plan, "dict"):
                        personalized_plan = personalized_plan.dict()
                    personalized_plan["materials"] = materials

            total_correct = gemini_resp.get("total_score", total_correct)
            total_qs = gemini_resp.get("total_questions", total_qs)

        return GradeResponse(
            total_score=total_correct,
            total_questions=total_qs,
            per_question=per_q,
            skill_summary=skill_summary,
            weak_topics=weak_topics,
            recommendations=recommendations,
            personalized_plan=personalized_plan,
            current_level=gemini_resp.get("current_level", req.profile.current_level if req.profile else "Unknown"),
            post_test_level=gemini_resp.get("post_test_level", "Unknown")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
