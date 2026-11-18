from sqlalchemy import or_, select
from sqlalchemy.orm import Session as DBSession

from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryUpdate


class MemoryService:
    """
    Handles creation, retrieval, updating, and deletion
    of user memories.
    """

    def __init__(self, db: DBSession):
        self.db = db

    # ========================================================
    # CREATE / UPSERT MEMORY
    # ========================================================

    def create_memory(
        self,
        user_id: int,
        payload: MemoryCreate,
    ) -> Memory:

        # ----------------------------------------------------
        # Normalize incoming values
        # ----------------------------------------------------

        memory_type = payload.memory_type.strip()
        key = payload.key.strip()
        value = payload.value.strip()
        source = payload.source.strip()

        # ----------------------------------------------------
        # Validate values
        # ----------------------------------------------------

        if not memory_type:
            raise ValueError("Memory type cannot be empty.")

        if not key:
            raise ValueError("Memory key cannot be empty.")

        if not value:
            raise ValueError("Memory value cannot be empty.")

        if not source:
            raise ValueError("Memory source cannot be empty.")

        # ----------------------------------------------------
        # Check whether this memory already exists
        #
        # Identity:
        # user_id + memory_type + key
        # ----------------------------------------------------

        existing_memory = self.db.scalar(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.memory_type == memory_type,
                Memory.key == key,
            )
        )

        # ----------------------------------------------------
        # EXISTING MEMORY → UPDATE
        # ----------------------------------------------------

        if existing_memory:

            existing_memory.value = value
            existing_memory.importance = payload.importance
            existing_memory.confidence = payload.confidence
            existing_memory.source = source

            self.db.commit()
            self.db.refresh(existing_memory)

            return existing_memory

        # ----------------------------------------------------
        # NEW MEMORY → CREATE
        # ----------------------------------------------------

        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            key=key,
            value=value,
            importance=payload.importance,
            confidence=payload.confidence,
            source=source,
        )

        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        return memory

    # ========================================================
    # LIST MEMORIES
    # ========================================================

    def list_memories(
        self,
        user_id: int,
        memory_type: str | None = None,
    ) -> list[Memory]:

        query = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(
                Memory.importance.desc(),
                Memory.updated_at.desc(),
            )
        )

        if memory_type:
            query = query.where(
                Memory.memory_type == memory_type.strip()
            )

        return list(
            self.db.scalars(query).all()
        )

    # ========================================================
    # GET MEMORY
    # ========================================================

    def get_memory(
        self,
        user_id: int,
        memory_id: int,
    ) -> Memory | None:

        return self.db.scalar(
            select(Memory).where(
                Memory.id == memory_id,
                Memory.user_id == user_id,
            )
        )

    # ========================================================
    # RETRIEVE RELEVANT MEMORIES
    # ========================================================

    def retrieve_relevant_memories(
        self,
        user_id: int,
        query_text: str,
        limit: int = 10,
    ) -> list[Memory]:

        query_text = query_text.strip()

        # ----------------------------------------------------
        # No query → return important memories
        # ----------------------------------------------------

        if not query_text:

            query = (
                select(Memory)
                .where(Memory.user_id == user_id)
                .order_by(
                    Memory.importance.desc(),
                    Memory.updated_at.desc(),
                )
                .limit(limit)
            )

            return list(
                self.db.scalars(query).all()
            )

        # ----------------------------------------------------
        # Extract useful words
        # ----------------------------------------------------

        words = {
            word.strip(".,!?;:()[]{}\"'").lower()
            for word in query_text.split()
            if len(
                word.strip(".,!?;:()[]{}\"'")
            ) >= 3
        }

        if not words:

            return self.list_memories(
                user_id=user_id
            )[:limit]

        # ----------------------------------------------------
        # Build keyword conditions
        # ----------------------------------------------------

        conditions = []

        for word in words:

            pattern = f"%{word}%"

            conditions.extend(
                [
                    Memory.memory_type.ilike(pattern),
                    Memory.key.ilike(pattern),
                    Memory.value.ilike(pattern),
                ]
            )

        # ----------------------------------------------------
        # Search only this user's memories
        # ----------------------------------------------------

        query = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                or_(*conditions),
            )
            .order_by(
                Memory.importance.desc(),
                Memory.confidence.desc(),
                Memory.updated_at.desc(),
            )
            .limit(limit)
        )

        return list(
            self.db.scalars(query).all()
        )

    # ========================================================
    # UPDATE MEMORY
    # ========================================================

    def update_memory(
        self,
        user_id: int,
        memory_id: int,
        payload: MemoryUpdate,
    ) -> Memory | None:

        memory = self.get_memory(
            user_id=user_id,
            memory_id=memory_id,
        )

        if not memory:
            return None

        update_data = payload.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            if isinstance(value, str):

                value = value.strip()

                if not value:
                    raise ValueError(
                        f"{field} cannot be empty."
                    )

            setattr(memory, field, value)

        self.db.commit()
        self.db.refresh(memory)

        return memory

    # ========================================================
    # DELETE MEMORY
    # ========================================================

    def delete_memory(
        self,
        user_id: int,
        memory_id: int,
    ) -> bool:

        memory = self.get_memory(
            user_id=user_id,
            memory_id=memory_id,
        )

        if not memory:
            return False

        self.db.delete(memory)
        self.db.commit()

        return True