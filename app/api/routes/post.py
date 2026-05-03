from typing import Any

from fastapi import Depends, HTTPException, status
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import APIRouterV1
from app.auth.permissions import require_permission
from app.db.post import SQLAlchemyPostDatabase, get_post_db
from app.models.user import User
from app.schemas.post import PostCreate, PostPayload, PostUpdate

router = APIRouterV1(prefix="/posts", tags=["Posts"])
tracer = trace.get_tracer("app.api.routes.post")


@router.post("/", response_model=PostPayload)
async def create_post(
    post_create: PostCreate,
    current_user: User = Depends(
        require_permission("post:create"),
    ),
    db: SQLAlchemyPostDatabase = Depends(get_post_db),
) -> Any:
    with tracer.start_as_current_span("posts.create_post") as span:
        span.set_attribute("current_user.id", str(current_user.id))
        try:
            post = await db.create(current_user.id, post_create)
            span.set_status(Status(StatusCode.OK))
            span.set_attribute("post.id", post.id)
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
    "/{id}",
    response_model=PostPayload,
    dependencies=[
        Depends(
            require_permission("post:read"),
        )
    ],
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


@router.patch(
    "/{id}",
    response_model=PostPayload,
)
async def update_post(
    id: int,
    post_update: PostUpdate,
    current_user: User = Depends(
        require_permission("post:update"),
    ),
    db: SQLAlchemyPostDatabase = Depends(get_post_db),
) -> Any:
    with tracer.start_as_current_span("posts.update_post") as span:
        span.set_attribute("post.id", id)
        span.set_attribute("current_user.id", str(current_user.id))

        update_data = post_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        post = await db.get(id)
        if post is None:
            span.set_status(Status(StatusCode.ERROR, "Post not found"))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        if post.created_by_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post",
            )

        try:
            updated_post = await db.update(post, update_data)
            span.set_status(Status(StatusCode.OK))
            return updated_post
        except SQLAlchemyError as e:
            span.record_exception(e)
            span.set_status(
                StatusCode.ERROR,
                "Database error occurred while updating post",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post due to a database error",
            ) from e
        except Exception as e:
            span.record_exception(e)
            span.set_status(
                StatusCode.ERROR,
                f"Unexpected error: {type(e).__name__}",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post due to an unexpected error",
            ) from e
