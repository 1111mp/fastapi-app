from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.utils.typing import StrOrList, normalize_to_list

from .deps import current_active_user


def require_role(required: StrOrList) -> Callable[..., Coroutine[Any, Any, User]]:
    """Require the user to have at least one of the specified roles."""
    required_roles = set(normalize_to_list(required))

    async def checker(user: User = Depends(current_active_user)) -> User:
        """Check if the user has at least one of the required roles."""
        if user.is_admin:
            return user

        user_roles = {role.name for role in user.roles}
        if not required_roles & user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role(s) to access this resource.",
            )

        return user

    return checker


def require_permission(required: StrOrList) -> Callable[..., Coroutine[Any, Any, User]]:
    """Require the user to have at least one of the specified permissions."""
    required_perms = set(normalize_to_list(required))

    async def checker(user: User = Depends(current_active_user)) -> User:
        """Check if the user has at least one of the required permissions."""
        if user.is_admin:
            return user

        user_perms = {p.code for role in user.roles for p in role.permissions}
        if not required_perms & user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required permission(s) to access this resource.",
            )

        return user

    return checker
