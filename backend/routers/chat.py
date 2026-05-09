from fastapi import APIRouter

from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse
from backend.services.llm_service import generate_message


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest) -> ChatMessageResponse:
    message = generate_message(
        user_message=request.message,
        system_prompt=request.system_prompt,
    )
    return ChatMessageResponse(message=message)
