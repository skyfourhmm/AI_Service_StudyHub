import os
import json
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Use the API key from env (do NOT hardcode). If you still need to use a direct key,
# set GEMINI_API_KEY in your .env to that key.
if not GEMINI_API_KEY:
    # Note: we don't raise here so unit tests can run without key if not calling gemini.
    pass

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def _build_prompt(payload: Dict[str, Any]) -> str:
    """
    Construct a robust prompt instructing Gemini to return ONLY valid JSON
    with the fields we need: total_score, per_question (with explain), skill_summary,
    weak_topics, recommendations, personalized_plan, proficiency_prediction, monitoring_alerts.
    """
    # We include payload json as a compact string to provide context
    profile = payload.get("profile", {})
    test_info = payload.get("test_info", {})
    answer_key = payload.get("answer_key", [])
    student_answers = payload.get("student_answers", {})
    test_history = profile.get("test_history", [])
    history_text = ""
    if test_history:
        history_text = "Student past test history (most recent first):\n"
        for t in test_history:
            # t should already include weak_topics and per_question if using new schema
            history_text += f"- Date: {t.get('test_date')}, Level: {t.get('level_at_test')}, Weak Topics: {t.get('weak_topics', [])}\n"

     # Detailed TOEIC/IELTS scales
    scales_text = (
        "Use this TOEIC scale strictly:\n"
        "10-250: Beginner (A1) -> very basic words/sentences\n"
        "255-400: Elementary (A2) -> short conversations, simple past/present\n"
        "405-600: Intermediate (B1) -> simple emails/reports, basic relative clauses\n"
        "605-780: Upper-Intermediate (B2) -> contracts, conditionals, passive, reasoning\n"
        "785-900: Advanced (C1) -> confident structures, professional vocab, tricky inference\n"
        "905-990: Proficiency (C2) -> near-native, complex context, high-speed tests\n\n"

        "Use this IELTS scale strictly:\n"
        "0-3.5: Beginner (A1-A2) -> basic communication, short reading/listening, simple writing\n"
        "4.0-5.0: Elementary (B1 low) -> familiar situations, short reading passages\n"
        "5.5-6.0: Intermediate (B1-B2) -> medium texts, basic essays, Reading 3-4 passages\n"
        "6.5-7.0: Upper-Intermediate (B2-C1) -> good academic communication, few grammar errors\n"
        "7.5-8.0: Advanced (C1) -> very good, occasional mistakes, academic journals\n"
        "8.5-9.0: Expert (C2) -> near-native, any complex academic content\n\n"
    )

    scales_text += (
        "// Valid TOEIC levels: '10-250', '255-400', '405-600', '605-780', '785-900', '905-990'\n"
        "// Valid IELTS levels: '0-3.5', '4.0-5.0', '5.5-6.0', '6.5-7.0', '7.5-8.0', '8.5-9.0'\n"
        "current_level and post_test_level must be exactly one of these strings.\n"
        "Do NOT use words like 'Intermediate', 'B1', 'Upper-Intermediate', 'Beginner', etc.\n"
    )

    prompt = (
        "You are an expert English learning coach and exam grader.\n"
        f"{scales_text}\n"
        f"{history_text}\n"
        f"Student Profile (without test_history): {json.dumps({k:v for k,v in profile.items() if k != 'test_history'})}\n"
        f"Student Test History: {json.dumps(test_history)}\n"
        "Analyze the student's answers and produce JSON ONLY with the exact schema below...\n"

        "Rules:\n"
        "- current_level must use student's profile score and map exactly to the tables.\n"
        "- post_test_level must be determined from the test score percentage and map exactly to the tables.\n"
        "- Do not use vague words like 'Intermediate'; always provide exact range string.\n\n"

        "REQUIRED OUTPUT SCHEMA:\n"
        "{\n"
        "  \"total_score\": int,\n"
        "  \"total_questions\": int,\n"
        "  \"per_question\": [{\n"
        "    \"id\": int, \"question\": string|null, \"correct\": bool, "
        "\"expected_answer\": string, \"user_answer\": string|null, "
        "\"skill\": string|null, \"topic\": string|null, \"explain\": string\n"
        "  }],\n"
        "  \"skill_summary\": [{\"skill\": string, \"total\": int, \"correct\": int, \"accuracy\": float}],\n"
        "  \"weak_topics\": [string],\n"
        "  \"recommendations\": [string],\n"
        # "  \"personalized_plan\": {\"progress_speed\": string, \"weekly_goals\": [{\"week\": int, \"topic\": string, \"description\": string, \"study_methods\": [string], \"materials\": [string], \"hours\": int}]},\n"
        " \"personalized_plan\": {\n"
        "   \"progress_speed\": {\n"
        "       \"category\": string, // e.g. 'steady', 'accelerating', 'declining', 'plateau'\n"
        "       \"description\": string, // qualitative summary\n"
        "       \"trend\": {\n"
        "           \"past_tests\": int,\n"
        "           \"accuracy_growth_rate\": float,\n"
        "           \"strong_skills\": [string],\n"
        "           \"weak_skills\": [string],\n"
        "           \"consistency_index\": float\n"
        "       },\n"
        "       \"predicted_reach_next_level_weeks\": int,\n"
        "       \"recommendation\": string\n"
        "   },\n"
        "   \"weekly_goals\": [{\"week\": int, \"topic\": string, \"description\": string, "
        "\"study_methods\": [string], \"materials\": [string], \"hours\": int}]\n"
        " },\n"   
        "\n"
        "Important:\n"
        "- The 'materials' field must only include values retrieved from the internal database mapping.\n"
        "- Use this mapping when suggesting materials:\n"
        "  Grammar → ['Grammar & Vocabulary Expansion - Trung cấp', 'Advanced Grammar Review & Traps in TOEIC']\n"
        "  Vocabulary → ['Essential Vocabulary - Chủ đề công việc', 'TOEIC Vocabulary Practice - Intermediate']\n"
        "  Listening → ['Listening Mastery – Chiến thuật nghe nâng cao', "
        "'Listening Practice A – TOEIC Part 3 & 4', 'Listening Starter – TOEIC Part 1 & 2']\n"
        "  Reading → ['Reading Mastery – Đọc hiểu & Suy luận ý chính', "
        "'Reading Practice A – TOEIC Part 6 & 7', 'Reading Starter – TOEIC Part 5 & 6']\n"
        "  Speaking → ['Speaking Workshop - Everyday Topics', 'Pronunciation & Fluency Training']\n"
        "- Do NOT invent or create new materials not in this list.\n"
        "\n"
        "  \"proficiency_prediction\": {\"skill_estimates\": [{\"skill\": string, "
        "\"current_level\": string, \"confidence\": string, \"predicted_gain_weeks\": int}]},\n"
        "  \"monitoring_alerts\": [string],\n"
        "  \"current_level\": string,\n"
        "  \"post_test_level\": string\n"
        "}\n\n"


        "Context:\n"
        f"Student Profile: {json.dumps(profile)}\n"
        f"Test Info: {json.dumps(test_info)}\n"
        f"Answer Key: {json.dumps(answer_key)}\n"
        f"Student Answers: {json.dumps(student_answers)}\n\n"

        "\nExample of correct fields:\n"
        '{\n'
        '  "current_level": "TOEIC 605-780",\n'
        '  "post_test_level": "TOEIC 10-250"\n'
        "}\n"
        "Use exactly this format for these two fields, no substitution with B1/B2/A1, etc.\n"

        "Produce JSON exactly following the schema. No extra commentary."
    )

    return prompt

def _extract_text_from_response(data: Dict[str, Any]) -> Optional[str]:
    """
    Given the raw HTTP response JSON from Gemini, attempt to extract the assistant text.
    Handles a few possible response shapes.
    """
    # Expected shape: data["candidates"][0]["content"]["parts"][0]["text"]
    try:
        # common current shape
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        # try other shapes: some models return "output" or "result"
        # best-effort search for any string in nested dict
        def find_str(obj):
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                for v in obj.values():
                    res = find_str(v)
                    if res:
                        return res
            if isinstance(obj, list):
                for item in obj:
                    res = find_str(item)
                    if res:
                        return res
            return None
        return find_str(data)

async def call_gemini_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async version: Send payload to Gemini and return parsed JSON following the REQUIRED OUTPUT SCHEMA.
    Raises RuntimeError if GEMINI_API_KEY is missing or response is invalid.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment; cannot call Gemini")

    prompt_text = _build_prompt(payload)
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    timeout = httpx.Timeout(
        connect=10.0,   # thời gian chờ kết nối
        read=120.0,     # chờ dữ liệu phản hồi
        write=30.0,     # ghi dữ liệu request
        pool=10.0       # lấy connection từ pool
    )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=body)
            print(f"DEBUG: Gemini response status code: {resp.status_code}")
            resp.raise_for_status()
    except httpx.RequestError as re:
        raise RuntimeError(f"Network error when calling Gemini: {re}")
    except httpx.HTTPStatusError as he:
        raise RuntimeError(f"Bad response from Gemini: {he.response.status_code} - {he}")

    data = resp.json()
    text_output = _extract_text_from_response(data)
    if not text_output:
        raise RuntimeError(f"Could not extract text from Gemini response. Full response: {json.dumps(data)[:2000]}")

    # clean code fences and leading/trailing markers
    text_output = text_output.strip()
    if text_output.startswith("```"):
        # remove triple backticks and possible language hint
        # e.g. ```json\n{...}\n```
        # strip leading backticks, then if starts with json remove, then strip
        text_output = text_output.strip("`").lstrip("json").strip()

    # final parse
    try:
        parsed = json.loads(text_output)
        # minimal validation: must contain total_score and per_question
        if not isinstance(parsed, dict) or "per_question" not in parsed or "total_score" not in parsed:
            raise RuntimeError(f"Gemini returned JSON but schema mismatch. Parsed keys: {list(parsed.keys())}")
        return parsed
    except json.JSONDecodeError as e:
        # return helpful debug info
        raise RuntimeError(f"Failed to parse JSON from Gemini output: {e}\nOutput:\n{text_output[:4000]}")
