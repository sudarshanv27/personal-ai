from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationListItem,
    ConversationResponse,
    ConversationUpdate,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


# ============================================================
# CREATE CONVERSATION
# ============================================================

@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    conversation = Conversation(
        user_id=current_user.id,
        title=payload.title.strip(),
        system_prompt=payload.system_prompt,
    )

    if not conversation.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation title cannot be empty",
        )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


# ============================================================
# LIST USER CONVERSATIONS
# ============================================================

@router.get(
    "",
    response_model=list[ConversationListItem],
)
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    conversations = db.scalars(
        select(Conversation)
        .where(
            Conversation.user_id == current_user.id
        )
        .order_by(
            Conversation.updated_at.desc()
        )
    ).all()

    return conversations


# ============================================================
# GET SINGLE CONVERSATION
# ============================================================

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


# ============================================================
# UPDATE / RENAME CONVERSATION
# ============================================================

@router.put(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: int,
    payload: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    new_title = payload.title.strip()

    if not new_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation title cannot be empty",
        )

    conversation.title = new_title

    db.commit()
    db.refresh(conversation)

    return conversation


# ============================================================
# DELETE CONVERSATION
# ============================================================

@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    db.delete(conversation)
    db.commit()

    return None