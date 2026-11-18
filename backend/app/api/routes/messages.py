import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"],
)


# ============================================================
# GET USER'S CONVERSATION
# ============================================================

def get_user_conversation(
    conversation_id: int,
    current_user: User,
    db: DBSession,
) -> Conversation:

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
# CREATE MESSAGE + COMPLETE AI RESPONSE
# ============================================================

@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    conversation_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """
    Create a user message and generate a complete AI response.
    """

    conversation = get_user_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )

    chat_service = ChatService(db)

    try:
        assistant_message = chat_service.generate_reply(
            conversation=conversation,
            user_id=current_user.id,
            user_message=payload.content,
        )

        return assistant_message

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}",
        )


# ============================================================
# STREAM MESSAGE USING SERVER-SENT EVENTS
# ============================================================

@router.post("/stream")
def create_message_stream(
    conversation_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """
    Create a user message and stream the AI response
    using Server-Sent Events (SSE).
    """

    conversation = get_user_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )

    chat_service = ChatService(db)

    def generate():
        try:

            # ------------------------------------------------
            # STREAM CHAT SERVICE EVENTS
            # ------------------------------------------------

            for event in chat_service.generate_reply_stream(
                conversation=conversation,
                user_id=current_user.id,
                user_message=payload.content,
            ):

                event_type = event.get("type")

                # --------------------------------------------
                # TOKEN EVENT
                # --------------------------------------------

                if event_type == "token":

                    data = json.dumps(
                        {
                            "content": event["content"],
                        },
                        ensure_ascii=False,
                    )

                    yield (
                        "event: token\n"
                        f"data: {data}\n\n"
                    )

                # --------------------------------------------
                # DONE EVENT
                # --------------------------------------------

                elif event_type == "done":

                    data = json.dumps(
                        {
                            "message_id": event["message_id"],
                            "conversation_id": event[
                                "conversation_id"
                            ],
                            "model": event["model"],
                        },
                        ensure_ascii=False,
                    )

                    yield (
                        "event: done\n"
                        f"data: {data}\n\n"
                    )

        except Exception:

            # --------------------------------------------
            # SAFE ERROR EVENT
            # --------------------------------------------
            #
            # Do NOT expose Python exception details,
            # database errors, file paths, API details,
            # stack traces, etc. to the client.
            # --------------------------------------------

            error_data = json.dumps(
                {
                    "code": "AI_GENERATION_FAILED",
                    "message": "Unable to generate a response.",
                    "retryable": True,
                },
                ensure_ascii=False,
            )

            yield (
                "event: error\n"
                f"data: {error_data}\n\n"
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# GET ALL MESSAGES
# ============================================================

@router.get(
    "",
    response_model=list[MessageResponse],
)
def list_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """
    Return all messages belonging to a conversation.
    """

    conversation = get_user_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation.id
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    ).all()

    return messages


# ============================================================
# DELETE MESSAGE
# ============================================================

@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_message(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """
    Delete a specific message from a conversation.
    """

    conversation = get_user_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )

    message = db.scalar(
        select(Message).where(
            Message.id == message_id,
            Message.conversation_id == conversation.id,
        )
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    db.delete(message)
    db.commit()

    return None