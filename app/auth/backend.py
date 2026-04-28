from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from httpx_oauth.clients.github import GitHubOAuth2

from app.core.config import settings

cookie_transport = CookieTransport(
    cookie_max_age=3600,
    cookie_secure=settings.ENVIRONMENT == "production",
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=24 * 3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


github_oauth_client = GitHubOAuth2(
    settings.GITHUB_CLIENT_ID,
    settings.GITHUB_CLIENT_SECRET,
)
