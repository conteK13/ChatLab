import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


API_BASE_URL = os.getenv("CHATLAB_BACKEND_URL", "http://localhost:8000").rstrip("/")


def render_chat_tab() -> None:
    st.subheader("챗봇")

    system_prompt = st.text_area(
        "시스템 프롬프트",
        placeholder="필요할 때만 입력하세요.",
        height=100,
    )

    render_messages()

    user_message = st.chat_input("메시지를 입력하세요.")
    if not user_message:
        return

    add_message("user", user_message)

    with st.spinner("응답을 기다리는 중입니다."):
        response_message, error_message = send_message(user_message, system_prompt)

    if error_message:
        st.error(error_message)
        return

    add_message("assistant", response_message)
    st.rerun()


def render_messages() -> None:
    for message in get_messages():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def send_message(user_message: str, system_prompt: str) -> tuple[str, str | None]:
    payload = {"message": user_message}

    if system_prompt.strip():
        payload["system_prompt"] = system_prompt

    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/message",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return "", f"백엔드 요청에 실패했습니다. 서버가 실행 중인지 확인하세요. ({exc})"

    data = response.json()
    return data["message"], None


def get_messages() -> list[dict[str, str]]:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    return st.session_state.chat_messages


def add_message(role: str, content: str) -> None:
    get_messages().append({"role": role, "content": content})
