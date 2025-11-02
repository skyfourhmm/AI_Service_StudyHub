def generate_test_prompt(
    topic: str,
    question_types: list = None,
    num_questions: int = 10,
    exam_type: str = "TOEIC",             # "TOEIC" | "IELTS"
    score_range: str = None               # e.g. "TOEIC 405-600" | "IELTS 5.5-6.0"
):
    """
    topic: the overall topic to guide question creation (e.g., "present simple")
    question_types: ["multiple_choice", "fill_in_blank", "rearrange", "essay"]
    num_questions: number of questions to generate
    exam_type: TOEIC | IELTS
    score_range: exam score range (e.g., TOEIC 405-600, IELTS 6.5-7.0)
    """
    if question_types is None:
        question_types = ["multiple_choice", "fill_in_blank", "rearrange", "essay"]

    types_text = {
        "multiple_choice": "Multiple-choice (4 options)",
        "fill_in_blank": "Fill in the blank",
        "rearrange": "Sentence rearrangement",
        "essay": "Essay (short/long)"
    }

    chosen_types_text = ", ".join([types_text[t] for t in question_types if t in types_text])

    return f"""
You are an English teacher specialized in {exam_type}.
Generate {num_questions} questions under the general theme "{topic}" (theme is only for guidance).
The required question types: {chosen_types_text}.
Target exam level: {exam_type} {score_range}.

Requirements for EACH question:
- Vocabulary, grammar, and complexity must match the learner's {exam_type} {score_range} level:
  TOEIC:
    * 10–250 (A1): Very basic, simple sentences. Grammar: be, have, present simple.
    * 255–400 (A2): Short conversations, past/present simple. Part 1–2 easy.
    * 405–600 (B1): Emails, short reports. Relative clauses, perfect tenses. More traps in Part 5–6.
    * 605–780 (B2): Contracts, company notices. Conditionals, passive. More inference.
    * 785–900 (C1): Nearly all structures, professional vocabulary. Tricky traps, inference questions.
    * 905–990 (C2): Near-native, complex context. Full traps, high speed.
  IELTS:
    * 0–3.5 (A1–A2): Basic vocabulary, struggle in communication. Very short reading/listening, simple sentences in writing.
    * 4.0–5.0 (B1 low): Can handle familiar situations. Short texts, simple sentences.
    * 5.5–6.0 (B1–B2): Understand medium texts, basic essays. 3–4 longer passages, limited task 2 writing.
    * 6.5–7.0 (B2–C1): Academic communication, few grammar mistakes. Academic reading/listening, coherent essays.
    * 7.5–8.0 (C1): Very strong, minor errors. Academic journals, in-depth essays.
    * 8.5–9.0 (C2): Expert level, near-native. Any academic/complex content.
- Field "skill" must be derived from the question type:
    * multiple_choice → Grammar
    * fill_in_blank  → Grammar
    * rearrange      → Grammar
    * essay          → Writing
- Field "topic" must be a **list of subtopics/concepts specific to the question itself**, NOT the overall theme.
- Each question must have a real correct answer (not just "A/B/C/D").
- Provide a detailed explanation for why the answer is correct/incorrect.
- If multiple_choice: "options" must be a raw list of answers (no numbering or letters).

Return ONLY valid JSON in the following format:

{{
  "status": "success",
  "data": [
    {{
      "type": "multiple_choice",
      "skill": "Grammar",
      "topic": ["<subtopic-for-this-question>"],
      "question": "...",
      "options": ["option1", "option2", "option3", "option4"],
      "answer": "the correct option text",
      "explanation": "Detailed explanation..."
    }},
    ...
  ]
}}

DO NOT add extra text, DO NOT use markdown.
"""
