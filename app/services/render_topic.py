import os
import json
import re
from dotenv import load_dotenv
from google import genai
from app.prompts.prompt_topic import generate_test_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Bạn phải đặt GEMINI_API_KEY trong .env hoặc biến môi trường")

model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
client = genai.Client(api_key=api_key)


async def render_test(topic: str,
                      num_questions: int = 10,
                      question_types: list = None,
                      exam_type: str = "TOEIC",
                      score_range: str = None):

    prompt = generate_test_prompt(
        topic=topic,
        question_types=question_types,
        num_questions=num_questions,
        exam_type=exam_type,
        score_range=score_range
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        text = response.text.strip()

        # 🧹 Làm sạch kết quả: bỏ ```json ``` hoặc ``` ```
        clean_text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()

        # ✅ Cố gắng parse JSON lần 1
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSONDecodeError lần 1: {e}")
            # 🩹 Escape dấu ngoặc kép bên trong
            fixed_text = clean_text.replace('\n', '\\n')
            fixed_text = re.sub(r'(?<!\\)"(.*?)"(?=\s*[:,}])', lambda m: json.dumps(m.group(1)), fixed_text)
            try:
                data = json.loads(fixed_text)
            except Exception as e2:
                print("❌ JSONDecodeError lần 2:", e2)
                raise ValueError(f"Không parse được JSON từ Gemini:\n{clean_text}")

        return data

    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi Gemini hoặc xử lý dữ liệu: {str(e)}")
