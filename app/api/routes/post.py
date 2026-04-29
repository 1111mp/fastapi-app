from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy.exc import SQLAlchemyError

from app.auth.deps import current_active_user
from app.db.post import SQLAlchemyPostDatabase, get_post_db
from app.models.user import User
from app.schemas.post import PostCreate, PostPayload

router = APIRouter(prefix="/posts", tags=["Posts"])
tracer = trace.get_tracer("app.api.routes.post")


@router.post("/", response_model=PostPayload)
async def create_post(
    post_create: PostCreate,
    current_user: User = Depends(current_active_user),
    db: SQLAlchemyPostDatabase = Depends(get_post_db),
) -> Any:
    with tracer.start_as_current_span("posts.create_post") as span:
        span.set_attribute("user.id", str(current_user.id))
        try:
            post = await db.create(current_user.id, post_create)
            span.set_status(Status(StatusCode.OK))
            span.set_attribute("post.id", str(post.id))
            return post
        except SQLAlchemyError as e:
            span.record_exception(e)
            span.set_status(StatusCode.ERROR, "Database persistent layer error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post due to a database error",
            ) from e
        except Exception as e:
            span.record_exception(e)
            span.set_status(StatusCode.ERROR, f"Unexpected error: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post due to an unexpected error",
            ) from e


@router.get(
    "/{id}", response_model=PostPayload, dependencies=[Depends(current_active_user)]
)
async def get_post(
    id: int,
    db: SQLAlchemyPostDatabase = Depends(get_post_db),
) -> Any:
    with tracer.start_as_current_span("posts.get_post") as span:
        span.set_attribute("post.id", id)

        post = await db.get(id)

        span.set_attribute("post.found", post is not None)
        if post is None:
            span.set_status(Status(StatusCode.ERROR, "Post not found"))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        else:
            span.set_status(Status(StatusCode.OK))
            span.set_attribute("post.created_by_id", str(post.created_by_id))

        return post
