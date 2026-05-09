from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from backend.core.config import settings
from backend.tools import get_chatlab_tools


def generate_message(user_message: str, system_prompt: str | None = None) -> str:
    llm = ChatOpenAI(model=settings.openai_model)
    agent = create_agent(
        model=llm,
        tools=get_chatlab_tools(),
        system_prompt=system_prompt.strip() if system_prompt and system_prompt.strip() else None,
    )
    response = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return str(response["messages"][-1].content)
