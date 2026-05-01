from typing import Any, Mapping

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from exceptions.repository import RepositoryValidationError
from sa.models.base_model import Base


class BaseRepository[T: Base]:
    def __init__(self, model: type[T], updatable_fields: set[str]) -> None:
        self._model = model
        self._updatable_fields = frozenset[str](updatable_fields)

    async def _get_by_attr(
        self,
        attr: InstrumentedAttribute[Any],
        value: Any,
        session: AsyncSession,
    ) -> T | None:
        query = select(self._model).filter(attr == value)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, id: int, session: AsyncSession) -> T | None:
        return await session.get(self._model, id)

    async def create(
        self,
        data: Mapping[str, Any],
        session: AsyncSession,
    ) -> T:
        instance = self._model(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def update(
        self,
        instance: T,
        data: Mapping[str, Any],
        session: AsyncSession,
    ) -> T:
        unknown = set(data) - self._updatable_fields
        if unknown:
            raise RepositoryValidationError(unknown)

        for field, value in data.items():
            setattr(instance, field, value)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def update_by_id(
        self,
        id: int,
        data: Mapping[str, Any],
        session: AsyncSession,
    ) -> T | None:
        instance = await session.get(self._model, id)
        if instance is None:
            return None
        return await self.update(instance, data, session)

    async def delete(self, instance: T, session: AsyncSession) -> None:
        await session.delete(instance)
        await session.flush()

    async def delete_by_id(self, id: int, session: AsyncSession) -> bool:
        instance = await session.get(self._model, id)
        if instance is None:
            return False
        await self.delete(instance, session)
        return True
