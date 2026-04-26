from fastapi import APIRouter

from app.auth.backend import auth_backend, github_oauth_client
from app.auth.deps import fastapi_users
from app.core.config import settings
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])

# POST /auth/jwt/login & POST /auth/jwt/logout
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt")

# POST /auth/register
router.include_router(
    fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

# POST /auth/forgot-password & POST /auth/reset-password
router.include_router(fastapi_users.get_reset_password_router())

# POST /auth/verify & POST /auth/request-verify-token
router.include_router(fastapi_users.get_verify_router(UserRead))

router.include_router(
    fastapi_users.get_oauth_router(
        github_oauth_client, auth_backend, settings.SECRET_KEY
    ),
    prefix="/github",
)
