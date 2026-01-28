import streamlit as st
from openai import OpenAI
from prompts import SYSTEM_PROMPT
from guard import is_blocked, blocked_reply
import csv, os
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LOG_FILE = "data/logs.csv"
os.makedirs("data", exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["time", "mode", "question"])

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

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Nhập câu hỏi lập trình của em...")

def ask_ai(messages):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4
    )
    return res.choices[0].message.content

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
