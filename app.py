import streamlit as st
import google.generativeai as genai
from prompts import SYSTEM_PROMPT
from guard import is_blocked, blocked_reply
import csv, os
from datetime import datetime
from PyPDF2 import PdfReader

# ================== CONFIG ==================
st.set_page_config(page_title="THINKODE AI", page_icon="🧠")
st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

# ================== API KEY ==================
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ================== LOG ==================
LOG_FILE = "data/logs.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["time", "mode", "question"])

# ================== MODE ==================
mode = st.selectbox(
    "Chọn chế độ hỗ trợ:",
    [
        "Phân tích đề bài",
        "Gợi ý hướng tiếp cận",
        "Kiểm tra tư duy",
        "Đánh giá độ phức tạp"
    ]
)

# ================== PDF UPLOAD ==================
st.markdown("### 📎 Đính kèm đề bài (PDF, không bắt buộc)")
pdf_file = st.file_uploader(
    "Upload đề bài nếu có",
    type=["pdf"],
    label_visibility="collapsed"
)

pdf_text = ""
if pdf_file:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        pdf_text += page.extract_text() + "\n"

# ================== SESSION ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ================== INPUT ==================
user_input = st.chat_input("Nhập câu hỏi lập trình của em...")

def ask_ai(prompt):
    response = model.generate_content(prompt)
    return response.text

# ================== MAIN ==================
if user_input:
    st.chat_message("user").write(user_input)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now(), mode, user_input])

    if is_blocked(user_input):
        reply = blocked_reply()
    else:
        full_prompt = f"""
{SYSTEM_PROMPT}

CHẾ ĐỘ: {mode}

ĐỀ BÀI (nếu có PDF):
{pdf_text}

CÂU HỎI:
{user_input}
"""
        try:
            reply = ask_ai(full_prompt)
        except Exception as e:
            reply = f"❌ Lỗi hệ thống Gemini:\n{e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
