import streamlit as st
from google import genai
import os
import PyPDF2

# ==========================
# CONFIG PAGE
# ==========================
st.set_page_config(
    page_title="THINKODE AI",
    page_icon="🧠",
    layout="centered"
)

# ==========================
# STYLE
# ==========================
st.markdown("""
<style>
.stChatMessage {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# TITLE
# ==========================
st.title("🧠 THINKODE AI")
st.caption("Think before Code – Huấn luyện tư duy lập trình cho học sinh")

# ==========================
# LOAD API KEY
# ==========================
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong Streamlit Secrets")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.header("⚙️ Cấu hình")

    mode = st.selectbox(
        "Chế độ hỗ trợ",
        [
            "Phân tích đề bài",
            "Gợi ý hướng tiếp cận",
            "Kiểm tra tư duy",
            "Đánh giá độ phức tạp",
            "Chế độ HSG chuyên sâu"
        ]
    )

    temperature = st.slider(
        "Mức sáng tạo",
        0.0, 1.0, 0.3
    )

    if st.button("🗑 Reset hội thoại"):
        st.session_state.messages = []
        st.rerun()

# ==========================
# PDF UPLOAD
# ==========================
st.markdown("📎 **Đính kèm đề bài (PDF, không bắt buộc)**")

pdf_file = st.file_uploader(
    "Tải file PDF",
    type=["pdf"]
)

pdf_text = ""

if pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text + "\n"
    st.success("✅ Đã đọc nội dung PDF")

# ==========================
# CHAT STATE
# ==========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================
# GEMINI FUNCTION
# ==========================
def ask_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-1.0-pro",
            contents=prompt,
            config={
                "temperature": temperature
            }
        )
        return response.text
    except Exception as e:
        return f"❌ Lỗi Gemini:\n{str(e)}"

# ==========================
# USER INPUT
# ==========================
user_input = st.chat_input("Nhập câu hỏi lập trình của em...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    full_prompt = f"""
Bạn là THINKODE AI – trợ lý huấn luyện tư duy lập trình cho học sinh THPT chuyên.

CHẾ ĐỘ: {mode}

ĐỀ BÀI (nếu có PDF):
{pdf_text if pdf_text else "Không có PDF"}

CÂU HỎI:
{user_input}

YÊU CẦU:
- Không giải full ngay
- Hướng dẫn tư duy
- Phù hợp học sinh chuyên
- Trình bày rõ ràng
"""

    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích..."):
            reply = ask_gemini(full_prompt)
            st.write(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
