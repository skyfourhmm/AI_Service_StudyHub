def generate_test_prompt(
    current_level: str,
    toeic_score: int | None = None,
    weak_skills: list[str] | None = None,
    exam_type: str = "TOEIC",
    topics: list[str] | None = None,
    difficulty: str | None = None,
    question_ratio: str = "MCQ",
    num_questions: int = 15,
    time_limit: int | None = 20,
):
    weak_skills_str = ", ".join(weak_skills or [])
    topics_str = ", ".join(topics or [])

    return f"""
You are an experienced English exam designer for {exam_type} tests.

Generate {num_questions} {question_ratio} questions.
Each question must reflect the student's learning profile:

- Current level: {current_level}
- TOEIC score (if provided): {toeic_score or "N/A"}
- Weak skills: {weak_skills_str}
- Topics to practice: {topics_str}
- Difficulty preference: {difficulty or "same as level"}
- Question type: {question_ratio}
- Total test time: {time_limit or "N/A"} minutes

========================
**QUESTION REQUIREMENTS**
========================
1. Focus on accuracy and natural English at the learner’s level.
2. All questions must be relevant to the selected topics (grammar points or vocabulary sets).
3. The difficulty must adapt to the student's choice ("easier", "same", or "harder").
4. Use authentic contexts similar to TOEIC/IELTS (e.g., business emails, conversations, reports).
5. **Explanations must be detailed**, including:
   - Grammar rule or vocabulary meaning involved
   - Why the correct answer fits
   - Why other options are incorrect
6. Each question should assess the weak skills when possible (Grammar, Vocabulary).

========================
**RESPONSE FORMAT**
========================
Return ONLY valid JSON (no markdown, no comments).

{{
  "status": "success",
  "data": [
    {{
      "type": "{question_ratio}",
      "skill": "Grammar or Vocabulary",
      "topic": ["specific subtopic like 'Conditionals' or 'Business Vocabulary'"],
      "question": "The question text here...",
      "options": ["option1", "option2", "option3", "option4"],  # if MCQ
      "answer": "the correct answer text",
      "explanation": "Detailed step-by-step explanation of grammar/vocabulary usage and why others are wrong."
    }}
  ]
}}
"""
