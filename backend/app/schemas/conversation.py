from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str = Field(
        default="New Conversation",
        min_length=1,
        max_length=255,
    )

    system_prompt: str | None = Field(
        default=None,
        max_length=10000,
    )


class ConversationUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    system_prompt: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ConversationListItem(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )