from fastapi import APIRouter, Depends

from app.auth.deps import current_active_user
from app.db.post import SQLAlchemyPostDatabase, get_post_db
from app.models.user import User
from app.schemas.post import PostCreate, PostPayload

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostPayload)
async def create_post(
    post_create: PostCreate,
    current_user: User = Depends(current_active_user),
    db: SQLAlchemyPostDatabase = Depends(get_post_db),
):
    return await db.create(current_user.id, post_create)


@router.get(
    "/{id}", response_model=PostPayload, dependencies=[Depends(current_active_user)]
)
async def get_post(
    id: int,
    db: SQLAlchemyPostDatabase = Depends(get_post_db),
):
    return await db.get(id)
