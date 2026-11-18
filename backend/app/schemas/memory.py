from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoryCreate(BaseModel):
    memory_type: str = Field(
        min_length=1,
        max_length=50,
    )

    key: str = Field(
        min_length=1,
        max_length=255,
    )

    value: str = Field(
        min_length=1,
        max_length=10000,
    )

    importance: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    confidence: int = Field(
        default=100,
        ge=0,
        le=100,
    )

    source: str = Field(
        default="user",
        min_length=1,
        max_length=100,
    )


class MemoryUpdate(BaseModel):
    memory_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    key: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    value: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000,
    )

    importance: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )

    confidence: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class MemoryResponse(BaseModel):
    id: int
    user_id: int
    memory_type: str
    key: str
    value: str
    importance: int
    confidence: int
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )