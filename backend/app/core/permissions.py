from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User


def require_owner(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow access only to the configured owner.
    """

    if current_user.id != settings.owner_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required",
        )

    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )

    return current_user