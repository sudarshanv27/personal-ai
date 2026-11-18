from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Memory(Base):
    __tablename__ = "memories"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "memory_type",
            "key",
            name="uq_memories_user_type_key",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    importance: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    confidence: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        default="user",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )