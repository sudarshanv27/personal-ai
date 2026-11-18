from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.conversation import Conversation
from app.services.chat_service import ChatService


db = SessionLocal()

try:
    conversation = db.scalar(
        select(Conversation)
        .where(Conversation.id == 1)
    )

    if not conversation:
        raise RuntimeError(
            "Conversation with ID 1 was not found."
        )

    chat_service = ChatService(db)

    print("\n--- CHAT SERVICE STREAM START ---\n")

    full_response = ""

    for chunk in chat_service.generate_reply_stream(
        conversation=conversation,
        user_message="Explain artificial intelligence in three short sentences.",
    ):
        print(chunk, end="", flush=True)
        full_response += chunk

    print("\n\n--- CHAT SERVICE STREAM END ---")

    print("\nFull response:")
    print(full_response)

finally:
    db.close()