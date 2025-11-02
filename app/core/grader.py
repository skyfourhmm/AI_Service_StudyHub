from collections import defaultdict
from typing import List, Dict
from app.core.schemas import QuestionKey, PerQuestionResult, SkillSummary

def grade_locally(answer_key: List[QuestionKey], student_answers: Dict[int, str]):
    total_correct = 0
    per_q: List[PerQuestionResult] = []
    skill_stats = defaultdict(lambda: {"correct": 0, "total": 0, "topics": defaultdict(int)})

    for q in answer_key:
        qid = q.id
        expected = q.answer.strip().upper() if q.answer else ""
        user_ans = student_answers.get(qid) or student_answers.get(str(qid))
        correct = (user_ans.strip().upper() == expected) if user_ans else False
        if correct:
            total_correct += 1

        explain_text = "Correct." if correct else f"Expected \"{expected}\" but got \"{(user_ans or 'no answer')}\"."

        per_q.append(PerQuestionResult(
            id=qid,
            question=getattr(q, "question", None),
            correct=correct,
            expected_answer=expected,
            user_answer=(user_ans.strip().upper() if user_ans else None),
            skill=q.skill,
            topic=q.topic,
            explain=explain_text
        ))

        # skill stats
        skill_key = q.skill or "Unknown"
        skill_stats[skill_key]["total"] += 1
        if correct:
            skill_stats[skill_key]["correct"] += 1
        if q.topic and not correct:
            skill_stats[skill_key]["topics"][q.topic] += 1

    # skill summary
    skill_summary = []
    weak_topics_grab = []
    for skill, st in skill_stats.items():
        total = st["total"]
        correct = st["correct"]
        accuracy = (correct / total * 100) if total > 0 else 0.0
        skill_summary.append(SkillSummary(skill=skill, total=total, correct=correct, accuracy=round(accuracy, 2)))
        sorted_topics = sorted(st["topics"].items(), key=lambda x: x[1], reverse=True)
        for tname, _ in sorted_topics[:2]:
            weak_topics_grab.append(f"{skill} - {tname}")

    seen = set()
    weak_topics = []
    for t in weak_topics_grab:
        if t not in seen:
            weak_topics.append(t)
            seen.add(t)
        if len(weak_topics) >= 3:
            break

    return total_correct, len(answer_key), per_q, skill_summary, weak_topics
