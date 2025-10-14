from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    context: list[str] | None = None
