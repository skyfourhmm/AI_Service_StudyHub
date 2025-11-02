# app/material_mapper.py

def get_materials_from_database(skill: str, weak_topics: list[str]):
    """
    Giả lập lấy dữ liệu từ DB hoặc mapping nội bộ.
    Trong thực tế bạn có thể truy vấn MongoDB, PostgreSQL, v.v.
    """
    # Mẫu dữ liệu nội bộ (bạn có thể thay bằng query DB)
    db_materials = {
        "Grammar": [
            "Grammar & Vocabulary Expansion - Trung cấp",
            "Advanced Grammar Review & Traps in TOEIC"
        ],
        "Vocabulary": [
            "Essential Vocabulary - Chủ đề công việc",
            "TOEIC Vocabulary Practice - Intermediate"
        ],
        "Listening": [
            "Listening Mastery – Chiến thuật nghe nâng cao",
            "Listening Practice A – TOEIC Part 3 & 4",
            "Listening Starter – TOEIC Part 1 & 2"
        ],
        "Reading": [
            "Reading Mastery – Đọc hiểu & Suy luận ý chính",
            "Reading Practice A – TOEIC Part 6 & 7",
            "Reading Starter – TOEIC Part 5 & 6"
        ],
        "Speaking": [
            "Speaking Workshop - Everyday Topics",
            "Pronunciation & Fluency Training"
        ]
    }

    # Tìm kỹ năng chính từ weak_topics nếu có
    key = skill or "Grammar"
    if key not in db_materials:
        key = "Grammar"

    return db_materials[key]
