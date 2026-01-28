import streamlit as st
import google.generativeai as genai
from prompts import SYSTEM_PROMPT
from guard import is_blocked, blocked_reply
import csv, os
from datetime import datetime

# =========================
# CONFIG GEMINI
# =========================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# LOG SETUP
# =========================
LOG_FILE = "data/logs.csv"
os.makedirs("data", exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["time", "mode", "question"])

# =========================
# UI
# =========================
st.set_page_config(page_title="THINKODE AI", page_icon="🧠")
st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

mode = st.selectbox(
    "Chọn chế độ hỗ trợ:",
    [
        "Phân tích đề bài",
        "Gợi ý hướng tiếp cận",
        "Kiểm tra tư duy",
        "Đánh giá độ phức tạp"
    ]
)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Nhập câu hỏi lập trình của em...")

# =========================
# GEMINI ASK FUNCTION
# =========================
def ask_ai(messages):
    """
    Gemini không dùng format role như OpenAI,
    nên ta GHÉP toàn bộ hội thoại thành 1 prompt.
    """
    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"[HỆ THỐNG]\n{m['content']}\n\n"
        elif m["role"] == "user":
            prompt += f"[HỌC SINH]\n{m['content']}\n\n"
        elif m["role"] == "assistant":
            prompt += f"[TRỢ GIẢNG]\n{m['content']}\n\n"

    response = model.generate_content(prompt)
    return response.text

# =========================
# MAIN CHAT LOGIC
# =========================
if user_input:
    st.chat_message("user").write(user_input)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now(), mode, user_input])

    if is_blocked(user_input):
        reply = blocked_reply()
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": f"CHẾ ĐỘ: {mode}\n{user_input}"
        })
        reply = ask_ai(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
