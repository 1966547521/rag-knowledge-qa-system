import streamlit as st
from agent.react_agent import ReactAgent
from utils.session_manager import SessionManager
from utils.geo_location import get_city_name
from utils.ui_components import (
    load_css, render_header, render_sidebar,
    render_thinking_animation, display_history_thinking
)

session_manager = SessionManager()

st.set_page_config(
    page_title="智扫通 · 智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

render_header()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "current_session_id" not in st.session_state:
    existing_sessions = session_manager.list_sessions()
    if existing_sessions:
        st.session_state["current_session_id"] = existing_sessions[0]["id"]
    else:
        session = session_manager.create_session(force=True)
        st.session_state["current_session_id"] = session["id"]


def load_session_messages():
    sid = st.session_state.get("current_session_id")
    if sid:
        s = session_manager.get_session(sid)
        st.session_state["message"] = list(s.get("messages", [])) if s else []
    else:
        st.session_state["message"] = []


if "message" not in st.session_state:
    load_session_messages()


render_sidebar(session_manager)

for msg in st.session_state["message"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("thinking"):
            display_history_thinking(msg["thinking"])
        st.write(msg["content"])

prompt = st.chat_input("输入您的问题，智能客服为您解答...")

if prompt:
    st.session_state["message"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    session_manager.save_message(
        st.session_state["current_session_id"], "user", prompt
    )

    get_city_name()

    collected_steps = []
    answer_text = ""

    thinking_spot = st.empty()
    answer_spot = st.empty()

    try:
        for event in st.session_state["agent"].execute_stream(prompt):
            if event["type"] == "thinking_steps":
                collected_steps = event["steps"]
                answer_spot.empty()
                with thinking_spot.container():
                    render_thinking_animation(collected_steps, is_complete=False)

            elif event["type"] == "answer_chunk":
                answer_text += event["content"]
                thinking_spot.empty()
                with answer_spot.container():
                    with st.chat_message("assistant"):
                        if collected_steps:
                            display_history_thinking(collected_steps)
                        st.write(answer_text)

    except Exception as e:
        answer_text = f"⚠️ 系统出现错误：{str(e)}"

    if not answer_text:
        answer_text = "抱歉，我暂时无法回答这个问题。"

    thinking_spot.empty()
    answer_spot.empty()

    st.session_state["message"].append({
        "role": "assistant",
        "content": answer_text,
        "thinking": collected_steps
    })

    session_manager.save_message(
        st.session_state["current_session_id"], "assistant", answer_text
    )

    st.rerun()
