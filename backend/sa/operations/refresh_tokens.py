from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from sa.models.users import RefreshTokenModel
from serializers.users import (
    RefreshTokenSchema,
)


async def record_refresh_token(
    session: AsyncSession, token_info: RefreshTokenSchema
) -> None:
    refresh_token_dict = token_info.model_dump()
    new_refresh_token = RefreshTokenModel(**refresh_token_dict)
    session.add(new_refresh_token)
    await session.flush()


async def delete_refresh_token(session: AsyncSession, token_id: UUID) -> bool:
    token = await session.get(RefreshTokenModel, token_id)
    if token:
        await session.delete(token)
        await session.flush()
        return True
    return False


async def delete_all_user_refresh_tokens(session: AsyncSession, user_id: int) -> None:
    query = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
    await session.execute(query)
    await session.flush()
