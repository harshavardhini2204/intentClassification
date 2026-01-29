import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:5000/analyze"

st.set_page_config(
    page_title="Psychological Assistant Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
# 🧠 Psychological Support Chat
Talk naturally with the assistant. It responds empathetically based on your emotional intent.
""")

st.sidebar.markdown("## About")
st.sidebar.info(
    """
This chatbot classifies your message into emotional intents such as:
**anger, depression, gratitude, greeting, loneliness, motivation, relationship, self_care, stress**,  
and provides empathetic guidance using a psychological assistant.
"""
)

if "messages" not in st.session_state:
    st.session_state.messages = []

INTENT_COLORS = {
    "stress": "#FFD6D6",
    "loneliness": "#E0E0FF",
    "gratitude": "#D6FFD6",
    "motivation": "#FFF8D6",
    "anger": "#FFC6C6",
    "depression": "#D6D6FF",
    "relationship": "#FFE6D6",
    "self_care": "#D6FFF0",
    "greeting": "#F0F0F0",
    "error": "#FFB6B6"
}

USER_BUBBLE_COLOR = "#DCF8C6"
USER_TEXT_COLOR = "#000000"

def send_message(user_text):
    try:
        response = requests.get(API_URL, params={"text": user_text})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"intent": "error", "confidence": 0, "response": f"API error: {e}"}

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...", placeholder="I feel stressed today...")
    submit_button = st.form_submit_button(label="Send")

if submit_button and user_input.strip():
    st.session_state.messages.append({
        "role": "user",
        "text": user_input,
        "time": datetime.now().strftime("%H:%M")
    })

    with st.spinner("Assistant is typing..."):
        data = send_message(user_input)
        st.session_state.messages.append({
            "role": "assistant",
            "text": data.get("response", "Sorry, something went wrong."),
            "intent": data.get("intent"),
            "confidence": data.get("confidence"),
            "time": datetime.now().strftime("%H:%M")
        })

st.markdown("<div style='height:700px; overflow-y:auto; padding:10px;'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    timestamp = msg.get("time", "")
    if msg["role"] == "user":
        st.markdown(
            f"<div style='text-align:right; background-color:{USER_BUBBLE_COLOR}; color:{USER_TEXT_COLOR}; "
            f"padding:12px; border-radius:12px; margin:6px 0; box-shadow:1px 2px 4px rgba(0,0,0,0.1)'>"
            f"{msg['text']}<br><span style='font-size:0.7em; color:gray; float:right'>{timestamp}</span></div>",
            unsafe_allow_html=True
        )
    else:
        bg_color = INTENT_COLORS.get(msg.get("intent", "error"), "#F1F0F0")
        st.markdown(
            f"<div style='text-align:left; background-color:{bg_color}; padding:12px; border-radius:12px; "
            f"margin:6px 0; box-shadow:1px 2px 4px rgba(0,0,0,0.1)'>"
            f"<b>Intent:</b> {msg.get('intent', '')} ({msg.get('confidence',0):.2f})<br>{msg['text']}<br>"
            f"<span style='font-size:0.7em; color:gray; float:right'>{timestamp}</span></div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)
