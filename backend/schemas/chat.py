from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    system_prompt: str | None = None


class ChatMessageResponse(BaseModel):
    message: str
