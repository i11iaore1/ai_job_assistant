from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sa.models import UserModel
from sa.models.users import RefreshTokenModel, UserProfileModel
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    RefreshTokenSchema,
    UpdateUserProfileSchema,
    UpdateUserSchema,
)


async def create_user(
    session: AsyncSession,
    user_info: CreateUserSchema,
) -> UserModel:
    new_user = UserModel(**user_info.model_dump())
    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)
    return new_user


async def get_user_by_id(
    session: AsyncSession, user_id: int, with_profile: bool = False
) -> UserModel | None:
    query = select(UserModel).filter(UserModel.id == user_id)
    if with_profile:
        query = query.options(joinedload(UserModel.profile))
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_by_email(
    session: AsyncSession, email: str, with_profile: bool = False
) -> UserModel | None:
    query = select(UserModel).filter(UserModel.email == email)
    if with_profile:
        query = query.options(joinedload(UserModel.profile))
    result = await session.execute(query)
    return result.scalars().first()


async def update_user(
    session: AsyncSession,
    user: UserModel,
    info_to_update: UpdateUserSchema,
) -> None:
    update_data = info_to_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await session.flush()
    await session.refresh(user)


async def delete_user(session: AsyncSession, user: UserModel) -> None:
    await session.delete(user)
    await session.flush()


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


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    profile_info: CreateUserProfileSchema,
) -> UserProfileModel:
    new_profile = UserProfileModel(user_id=user_id, **profile_info.model_dump())
    session.add(new_profile)
    await session.flush()
    await session.refresh(new_profile)
    return new_profile


async def get_profile_by_user_id(
    session: AsyncSession, user_id: int
) -> UserProfileModel | None:
    query = select(UserProfileModel).filter(UserProfileModel.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def update_user_profile(
    session: AsyncSession,
    profile: UserProfileModel,
    info_to_update: UpdateUserProfileSchema,
) -> None:
    update_data = info_to_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    await session.flush()
    await session.refresh(profile)
