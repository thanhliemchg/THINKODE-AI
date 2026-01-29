import streamlit as st
from google import genai
import os
import PyPDF2

# ================= CONFIG =================
st.set_page_config(
    page_title="THINKODE AI",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

# ================= API KEY =================
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ Chưa cấu hình GOOGLE_API_KEY")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ================= MODE =================
mode = st.selectbox(
    "🧠 Chọn chế độ hỗ trợ:",
    [
        "Phân tích đề bài",
        "Gợi ý hướng tiếp cận",
        "Kiểm tra tư duy",
        "Đánh giá độ phức tạp"
    ]
)

# ================= PDF =================
st.markdown("📎 **Đính kèm đề bài (PDF, không bắt buộc)**")
pdf_file = st.file_uploader(
    "",
    type=["pdf"],
    label_visibility="collapsed"
)

pdf_text = ""
if pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        if page.extract_text():
            pdf_text += page.extract_text() + "\n"

# ================= CHAT =================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Nhập câu hỏi lập trình của em...")

def ask_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-1.0-pro",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Lỗi Gemini:\n{e}"

if user_input:
    st.chat_message("user").write(user_input)

    full_prompt = f"""
Bạn là THINKODE AI – trợ lý huấn luyện tư duy lập trình cho học sinh.

CHẾ ĐỘ: {mode}

ĐỀ BÀI (PDF nếu có):
{pdf_text if pdf_text else "(Không có PDF)"}

CÂU HỎI:
{user_input}

Yêu cầu:
- Không giải ngay
- Phân tích tư duy
- Trình bày dễ hiểu
"""

    reply = ask_gemini(full_prompt)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    st.chat_message("assistant").write(reply)
