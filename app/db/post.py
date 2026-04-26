from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.db import get_async_session
from app.models.post import Post
from app.schemas.post import PostCreate


class SQLAlchemyPostDatabase:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get(self, post_id: int) -> Post | None:
        statement = select(Post).where(Post.id == post_id)
        return await self._get_post(statement)

    async def get_by_user(self, user_id: int) -> list[Post]:
        results = await self.session.execute(
            select(Post).where(Post.created_by_id == user_id)
        )
        return list(results.scalars().all())

    async def create(self, user_id: UUID, post_create: PostCreate) -> Post:
        post = Post(
            title=post_create.title,
            content=post_create.content,
            created_by_id=user_id,
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)
        await self.session.commit()

    async def _get_post(self, statement: Select) -> Post | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


async def get_post_db(
    session: AsyncSession = Depends(get_async_session),
):
    yield SQLAlchemyPostDatabase(session)
