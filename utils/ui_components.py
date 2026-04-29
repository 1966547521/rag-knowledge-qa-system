"""
UI组件模块 - CSS样式、侧边栏渲染、思考过程动画、版本信息
"""
import streamlit as st
from utils.geo_location import get_geo_status, get_city_name

VERSION = "v2.2"


def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', 'Microsoft YaHei', sans-serif;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0e27 0%, #101535 30%, #0f1738 60%, #0a0f2c 100%) !important;
        }
        section[data-testid="stSidebar"] * {
            color: #c8d6e5 !important;
        }
        section[data-testid="stSidebar"] h3 {
            color: #a0b4ff !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(99, 130, 220, 0.2) !important;
        }
        section[data-testid="stSidebar"] small, section[data-testid="stSidebar"] .stCaptionContainer p {
            color: #7889a4 !important;
        }
        section[data-testid="stSidebar"] .stTextInput > label {
            color: #a0b4ff !important;
            font-size: 0.8rem;
        }
        section[data-testid="stSidebar"] input {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(99,130,220,0.25) !important;
            color: #e0e6f0 !important;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] input:focus {
            border-color: rgba(99,130,220,0.5) !important;
            box-shadow: 0 0 0 2px rgba(99,130,220,0.15) !important;
        }
        section[data-testid="stSidebar"] input::placeholder {
            color: #556080 !important;
        }

        section[data-testid="stSidebar"] button {
            background: rgba(99, 130, 220, 0.08) !important;
            border: 1px solid rgba(99, 130, 220, 0.18) !important;
            border-radius: 10px !important;
            color: #a0b4ff !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] button:hover {
            background: rgba(99, 130, 220, 0.2) !important;
            border-color: rgba(99, 130, 220, 0.4) !important;
            color: #c8d6ff !important;
            box-shadow: 0 0 12px rgba(99, 130, 220, 0.2);
        }
        section[data-testid="stSidebar"] button[kind="primary"] {
            background: rgba(99, 130, 220, 0.2) !important;
            border-color: rgba(99, 130, 220, 0.4) !important;
            color: #d0dcff !important;
            box-shadow: 0 0 10px rgba(99, 130, 220, 0.15);
        }
        section[data-testid="stSidebar"] .stColumn:last-child button {
            min-width: 30px !important;
            width: 30px !important;
            height: 30px !important;
            padding: 0 !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            line-height: 1 !important;
            background: rgba(220, 80, 80, 0.1) !important;
            border-color: rgba(220, 80, 80, 0.2) !important;
            color: #f08080 !important;
        }
        section[data-testid="stSidebar"] .stColumn:last-child button:hover {
            background: rgba(220, 80, 80, 0.25) !important;
            border-color: rgba(220, 80, 80, 0.45) !important;
            color: #ff9090 !important;
            box-shadow: 0 0 8px rgba(220, 60, 60, 0.25);
        }

        .main-header-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 22px 30px;
            margin-bottom: 16px;
        }
        .main-header-card h1 {
            color: #ffffff;
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0 0 4px 0;
            padding: 0;
        }
        .main-header-card p {
            color: rgba(255,255,255,0.85);
            font-size: 0.88rem;
            margin: 0;
            font-weight: 400;
        }

        .geo-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.7rem;
            margin: 6px 0;
        }
        .geo-badge.granted {
            background: rgba(46, 204, 113, 0.12);
            color: #2ecc71;
        }
        .geo-badge.manual {
            background: rgba(241, 196, 15, 0.12);
            color: #f1c40f;
        }
        .geo-badge.pending {
            background: rgba(231, 76, 60, 0.12);
            color: #e74c3c;
        }

        .version-tag {
            position: fixed;
            bottom: 0;
            left: 0;
            z-index: 999;
            font-size: 0.65rem;
            color: #4a5580;
            text-align: center;
            padding: 8px 16px;
            background: linear-gradient(180deg, rgba(10, 14, 39, 0) 0%, rgba(10, 14, 39, 0.95) 30%, rgba(10, 14, 39, 1) 100%);
            pointer-events: none;
        }

        @keyframes thinking-pulse {
            0%, 100% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.02); }
        }
        .thinking-active {
            animation: thinking-pulse 1.2s ease-in-out infinite;
        }

        div[data-testid="stStatus"] {
            background: rgba(99, 130, 220, 0.06) !important;
            border: 1px solid rgba(99, 130, 220, 0.15) !important;
            border-radius: 12px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown(f"""
    <div class="main-header-card">
        <h1>🤖 智扫通 · 机器人智能客服</h1>
        <p>AI驱动的扫地机器人智能助手 · 知识问答 · 使用报告 · 天气查询</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar(session_manager):
    with st.sidebar:
        st.markdown("### 💬 会话管理")

        if st.button("➕ 新建会话", use_container_width=True, key="new_chat_btn"):
            if session_manager.has_empty_session():
                st.toast("已存在空会话，无需重复创建", icon="⚠️")
            else:
                new_session = session_manager.create_session(force=True)
                st.session_state["current_session_id"] = new_session["id"]
                st.session_state["message"] = []
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        sessions = session_manager.list_sessions()
        st.caption(f"共 {len(sessions)} 个会话")

        current_sid = st.session_state.get("current_session_id", "")

        for s in sessions:
            sid = s["id"]
            is_active = sid == current_sid
            msg_count = session_manager.get_message_count(sid)
            name = s.get("name", "未命名")
            if len(name) > 11:
                name = name[:11] + "…"

            prefix = "🟢" if is_active else "⚪"
            btn_label = f"{prefix} {name}"

            row = st.container()
            c1, c2 = row.columns([11, 1])
            with c1:
                if st.button(
                    btn_label,
                    key=f"sel_{sid}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    help=f"消息数: {msg_count}"
                ):
                    switch_session(sid, session_manager)
                    st.rerun()
            with c2:
                if st.button(
                    "✕",
                    key=f"del_{sid}",
                    use_container_width=True,
                    help="删除此会话"
                ):
                    session_manager.delete_session(sid)
                    if current_sid == sid:
                        remaining = session_manager.list_sessions()
                        if remaining:
                            switch_session(remaining[0]["id"], session_manager)
                        else:
                            new_s = session_manager.create_session(force=True)
                            switch_session(new_s["id"], session_manager)
                    st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        geo = get_geo_status()
        badge_class = geo["status"]
        st.markdown(f"""
        <div class="geo-badge {badge_class}">
            <span>📍</span><span>{geo['text']}</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("⚙️ 位置与天气设置", expanded=False):
            auto_city = get_city_name()
            default_city = st.session_state.get("_manual_city", auto_city)

            manual_city = st.text_input(
                "设置城市",
                value=default_city,
                placeholder="例如：北京、上海",
                key="manual_city_widget"
            )
            if manual_city or manual_city == "":
                if manual_city != st.session_state.get("_manual_city", ""):
                    st.session_state["_manual_city"] = manual_city.strip()
                    st.rerun()

            manual_weather = st.text_input(
                "设置天气（可选）",
                value=st.session_state.get("_manual_weather", st.session_state.get("_auto_weather", "")),
                placeholder="例如：多云，25°C",
                key="manual_weather_widget"
            )
            if manual_weather != st.session_state.get("_manual_weather", ""):
                st.session_state["_manual_weather"] = manual_weather.strip()
                st.rerun()

            if st.button("🔄 清除手动设置"):
                st.session_state["_manual_city"] = ""
                st.session_state["_manual_weather"] = ""
                st.session_state.pop("_geo_city", None)
                st.session_state.pop("_auto_weather", None)
                st.rerun()

def switch_session(sid, session_manager):
    st.session_state["current_session_id"] = sid
    s = session_manager.get_session(sid)
    st.session_state["message"] = list(s.get("messages", [])) if s else []


def render_thinking_animation(steps: list[str], is_complete: bool = False):
    if not steps:
        return

    if is_complete:
        label = "✅ 思考过程（已完成）"
        state = "complete"
    else:
        label = "🤔 正在思考..."
        state = "running"

    container = st.status(label, state=state if not is_complete else "complete")
    with container:
        for i, step in enumerate(steps):
            if is_complete:
                st.caption(f"✓ {step}")
            else:
                st.caption(f"⏳ {step}")


def render_version():
    st.markdown(f"""
    <div class="version-tag">
        智扫通 {VERSION} · Powered by LangChain + RAG
    </div>
    """, unsafe_allow_html=True)


def display_history_thinking(steps: list[str]):
    if not steps:
        return
    with st.expander("✅ 思考过程", expanded=False):
        for i, step in enumerate(steps, 1):
            st.caption(f"{i}. {step}")
