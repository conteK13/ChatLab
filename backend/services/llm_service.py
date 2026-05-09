from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from backend.core.config import settings


def generate_message(user_message: str, system_prompt: str | None = None) -> str:
    llm = ChatOpenAI(model=settings.openai_model)
    messages = []

    if system_prompt and system_prompt.strip():
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=user_message))

    response = llm.invoke(messages)
    return str(response.content)
