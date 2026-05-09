from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from backend.core.config import settings
from backend.tools import get_chatlab_tools


def generate_message(user_message: str, system_prompt: str | None = None) -> str:
    tools = get_chatlab_tools()
    tools_by_name = {tool.name: tool for tool in tools}
    tool_call_llm = ChatOpenAI(model=settings.openai_model).bind_tools(tools)
    answer_llm = ChatOpenAI(model=settings.openai_model)
    messages = []

    if system_prompt and system_prompt.strip():
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=user_message))

    response = tool_call_llm.invoke(messages)

    if not response.tool_calls:
        return str(response.content)

    messages.append(response)

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        selected_tool = tools_by_name[tool_name]
        tool_result = selected_tool.invoke(tool_call["args"])
        messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
            )
        )

    final_response = answer_llm.invoke(messages)
    return str(final_response.content)
