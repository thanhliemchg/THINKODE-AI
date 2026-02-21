
import streamlit as st
from google import genai
import os
from datetime import datetime
import csv
import tempfile
import PyPDF2

st.set_page_config(
    page_title="THINKODE AI",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

os.makedirs("data", exist_ok=True)
LOG_FILE = "data/logs.csv"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["time", "mode", "question"])

mode = st.selectbox(
    "🧠 Chọn chế độ hỗ trợ:",
    [
        "Phân tích đề bài",
        "Gợi ý hướng tiếp cận",
        "Kiểm tra tư duy",
        "Đánh giá độ phức tạp"
    ]
)

st.markdown("### 📎 Đính kèm đề bài (PDF, không bắt buộc)")
uploaded_file = st.file_uploader("Upload file PDF", type=["pdf"])

pdf_text = ""

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    reader = PyPDF2.PdfReader(tmp_path)
    for page in reader.pages:
        if page.extract_text():
            pdf_text += page.extract_text() + "\n"

user_input = st.chat_input("💬 Nhập câu hỏi lập trình của em...")

def ask_ai(prompt):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config={
            "temperature": 0.4
        }
    )
    return response.text

if user_input:
    st.chat_message("user").write(user_input)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now(), mode, user_input])

    full_prompt = f"""
CHẾ ĐỘ: {mode}

ĐỀ BÀI (nếu có):
{pdf_text}

CÂU HỎI:
{user_input}
"""

    try:
        reply = ask_ai(full_prompt)
        st.chat_message("assistant").write(reply)
    except Exception as e:
        st.error(f"❌ Lỗi hệ thống Gemini: {e}")
