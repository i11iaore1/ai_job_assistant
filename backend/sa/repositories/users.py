from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, joinedload

from sa.models import UserModel
from sa.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self) -> None:
        super().__init__(model=UserModel, updatable_fields={"username"})

    async def get_by_id_with_profile(
        self,
        id: int,
        session: AsyncSession,
    ) -> UserModel | None:
        return await self._get_by_attr_with_profile(
            attr=UserModel.id,
            value=id,
            session=session,
        )

    async def get_by_email(
        self,
        email: str,
        session: AsyncSession,
    ) -> UserModel | None:
        return await self._get_by_attr(
            attr=UserModel.email,
            value=email,
            session=session,
        )

    async def _get_by_attr_with_profile(
        self,
        attr: InstrumentedAttribute[Any],
        value: Any,
        session: AsyncSession,
    ) -> UserModel | None:
        query = (
            select(UserModel)
            .filter(attr == value)
            .options(joinedload(UserModel.profile))
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_email_with_profile(
        self,
        email: str,
        session: AsyncSession,
    ) -> UserModel | None:
        return await self._get_by_attr_with_profile(
            attr=UserModel.email,
            value=email,
            session=session,
        )


user_repository = UserRepository()
