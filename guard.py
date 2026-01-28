BLOCK_KEYWORDS = [
    "viết code", "code hoàn chỉnh", "lời giải",
    "đáp án", "giải bài", "code giúp"
]

def is_blocked(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in BLOCK_KEYWORDS)

def blocked_reply():
    return (
        "THINKODE AI không giải bài thay em 🙂\n\n"
        "Ta cùng suy nghĩ nhé:\n"
        "• Đề bài cho những dữ kiện nào?\n"
        "• Kết quả cần đạt là gì?\n"
        "• Em thử mô tả thuật toán bằng lời xem sao."
    )
