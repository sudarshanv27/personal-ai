from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.memory import (
    MemoryCreate,
    MemoryResponse,
    MemoryUpdate,
)
from app.services.memory_service import MemoryService


router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    payload: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    service = MemoryService(db)

    try:
        return service.create_memory(
            user_id=current_user.id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[MemoryResponse],
)
def list_memories(
    memory_type: str | None = Query(
        default=None,
        max_length=50,
    ),
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    service = MemoryService(db)

    return service.list_memories(
        user_id=current_user.id,
        memory_type=memory_type,
    )


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
)
def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    service = MemoryService(db)

    memory = service.get_memory(
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    return memory


@router.put(
    "/{memory_id}",
    response_model=MemoryResponse,
)
def update_memory(
    memory_id: int,
    payload: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    service = MemoryService(db)

    try:
        memory = service.update_memory(
            user_id=current_user.id,
            memory_id=memory_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    return memory


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    service = MemoryService(db)

    deleted = service.delete_memory(
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    return None