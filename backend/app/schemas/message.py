from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=100000,
    )


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    model: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)