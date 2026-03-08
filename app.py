# app.py
import streamlit as st
import requests
import re
import time

# =======================
# CONFIG – Thay ở đây
# =======================
API_KEY = "YOUR_API_KEY"  # Thay bằng Arcana / Chat AI API key của bạn
ARCANA_ID = "quocvinh.vu/UserstestDesktopPraktikumsbericht_offiziell.pdf"  # Thay bằng Arcana ID của bạn
MODEL = "qwen3-30b-a3b-instruct-2507"
API_URL = "https://chat-ai.academiccloud.de/v1/chat/completions"
INFERENCE_SERVICE = "saia-openai-gateway"
# =======================

# Hàm clean output từ Arcana
def clean_arcana_output(raw_text):
    # chỉ lấy phần trước 'References:' nếu có
    if "References:" in raw_text:
        raw_text = raw_text.split("References:")[0]

    lines = raw_text.split("\n")
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # loại các dòng bắt đầu bằng [ hoặc ! hoặc --- hoặc toàn in hoa + số (PDF metadata)
        if line.startswith("[") or line.startswith("!") or line.startswith("---"):
            continue
        if line.isupper() and any(c.isdigit() for c in line):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines)

# Streamlit UI
st.set_page_config(page_title="Arcana Chatbot", page_icon="🤖")
st.title("🤖 Arcana Chatbot")
st.markdown("Chat với tài liệu của bạn. Multi-turn + output sạch + streaming kiểu ChatGPT.")

# State lưu conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input text
user_input = st.text_input("Bạn:", key="input")

if user_input:
    # append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # chuẩn bị payload cho Arcana API
    payload = {
        "model": MODEL,
        "messages": st.session_state.messages,
        "enable-tools": True,
        "arcana": {"id": ARCANA_ID}
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "inference-service": INFERENCE_SERVICE
    }

    # gửi request đến Arcana
    with st.spinner("Arcana đang trả lời..."):
        r = requests.post(API_URL, headers=headers, json=payload)
        if r.status_code != 200:
            st.error(f"Lỗi API: {r.status_code}\n{r.text}")
        else:
            raw_answer = r.json()["choices"][0]["message"]["content"]
            clean_answer = clean_arcana_output(raw_answer)
            st.session_state.messages.append({"role": "assistant", "content": clean_answer})
            
            # streaming: in từng dòng
            answer_placeholder = st.empty()
            answer_text = ""
            for line in clean_answer.split("\n"):
                answer_text += line + "\n"
                answer_placeholder.text(answer_text)
                time.sleep(0.05)  # tạo hiệu ứng streaming
