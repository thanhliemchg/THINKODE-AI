import streamlit as st
import google.generativeai as genai
import os, csv
from datetime import datetime
from PyPDF2 import PdfReader

# ================== CONFIG ==================
st.set_page_config(
    page_title="THINKODE AI",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

# ================== API KEY ==================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets")
    st.stop()

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash-latest"  # ✔️ MODEL ĐÚNG

# ================== LOG ==================
LOG_FILE = "data/logs.csv"
os.makedirs("data", exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["time", "mode", "question"])

# ================== MODE ==================
mode = st.selectbox(
    "🧠 Chọn chế độ hỗ trợ:",
    [
        "Phân tích đề bài",
        "Gợi ý hướng tiếp cận",
        "Kiểm tra tư duy",
        "Đánh giá độ phức tạp"
    ]
)

# ================== PDF UPLOAD ==================
st.markdown("📎 **Đính kèm đề bài (PDF, không bắt buộc)**")
pdf_file = st.file_uploader(
    "",
    type=["pdf"],
    accept_multiple_files=False
)

pdf_text = ""
if pdf_file:
    try:
        reader = PdfReader(pdf_file)
        pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        st.success("✅ Đã đọc nội dung PDF")
    except:
        st.error("❌ Không đọc được file PDF")

# ================== CHAT ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("💬 Nhập câu hỏi lập trình của em...")

# ================== GEMINI ==================
def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Lỗi hệ thống Gemini:** {str(e)}"

# ================== HANDLE INPUT ==================
if user_input:
    st.chat_message("user").write(user_input)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now(), mode, user_input])

    full_prompt = f"""
Bạn là THINKODE AI – trợ lý huấn luyện tư duy lập trình cho học sinh.

CHẾ ĐỘ: {mode}

ĐỀ BÀI (nếu có từ PDF):
{pdf_text}

CÂU HỎI:
{user_input}

YÊU CẦU:
- Không giải ngay
- Ưu tiên phân tích, tư duy
- Phù hợp học sinh THCS – THPT
"""

    reply = ask_gemini(full_prompt)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.chat_message("assistant").write(reply)
