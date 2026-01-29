import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os, tempfile

# ================= CONFIG =================
st.set_page_config(
    page_title="THINKODE AI",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

# ================= API =================
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ Chưa cấu hình GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= SETTINGS =================
mode = st.selectbox(
    "🧠 Chế độ hỗ trợ",
    [
        "Phân tích đề bài",
        "Gợi ý thuật toán",
        "Viết lời giải chi tiết",
        "Sinh test & kiểm tra",
        "HSG / Olympic Tin"
    ]
)

# ================= PDF INPUT =================
st.subheader("📎 Đính kèm đề bài (PDF, không bắt buộc)")
pdf = st.file_uploader("Upload PDF", type="pdf")

pdf_text = ""
if pdf:
    reader = PdfReader(pdf)
    for p in reader.pages:
        pdf_text += p.extract_text() + "\n"

# ================= CHAT UI =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Nhập câu hỏi lập trình / đề bài…")

# ================= RUN =================
if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("🤖 THINKODE AI đang suy nghĩ..."):

            level = "NÂNG CAO – HSG, Olympic Tin, tư duy thuật toán"
            if mode != "HSG / Olympic Tin":
                level = "PHỔ THÔNG – THCS & THPT"

            prompt = f"""
Bạn là trợ lý AI huấn luyện tư duy lập trình.

CHẾ ĐỘ: {mode}
MỨC ĐỘ: {level}

ĐỀ BÀI:
{question}

NỘI DUNG PDF (nếu có):
{pdf_text}

YÊU CẦU:
- Giải thích rõ ràng
- Có tư duy, phân tích
- Nếu là HSG: nêu hướng tối ưu, độ phức tạp
- Trình bày mạch lạc, dễ học
"""

            response = model.generate_content(prompt)
            answer = response.text
            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

# ================= EXPORT PDF =================
if st.session_state.messages:
    if st.button("📄 Xuất toàn bộ lời giải ra PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            doc = SimpleDocTemplate(tmp.name)
            styles = getSampleStyleSheet()
            story = []

            for m in st.session_state.messages:
                role = "HỌC SINH" if m["role"] == "user" else "THINKODE AI"
                story.append(Paragraph(f"<b>{role}:</b><br/>{m['content']}", styles["Normal"]))

            doc.build(story)
            st.success("✅ Đã tạo PDF")

            with open(tmp.name, "rb") as f:
                st.download_button(
                    "⬇️ Tải PDF",
                    f,
                    file_name="thinkode_ai_solution.pdf"
                )
