# render_service.py

import os
import json
import asyncio
from dotenv import load_dotenv
from google import genai
from app.prompts.prompt_custom import generate_test_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("You must set GEMINI_API_KEY in your .env file or environment variables.")

model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
client = genai.Client(api_key=api_key)


async def render_test(
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
    prompt = generate_test_prompt(
        current_level=current_level,
        toeic_score=toeic_score,
        weak_skills=weak_skills,
        exam_type=exam_type,
        topics=topics,
        difficulty=difficulty,
        question_ratio=question_ratio,
        num_questions=num_questions,
        time_limit=time_limit,
    )

    try:
        # Dùng asyncio.to_thread để chạy lệnh đồng bộ trong async context
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents=prompt
        )

        text = response.text.strip()
        
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()

        data = json.loads(text)
        return data

    except json.JSONDecodeError:
        raise ValueError(f"❌ Failed to parse JSON from Gemini. Raw response:\n{text}")
    except Exception as e:
        raise RuntimeError(f"⚠️ Error calling Gemini API: {str(e)}")
