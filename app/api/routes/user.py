from fastapi import APIRouter

from app.auth.deps import fastapi_users
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
