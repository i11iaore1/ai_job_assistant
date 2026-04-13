from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sa_service.models import UserModel
from serializers.users import CreateUserSchema


class EmailExists(Exception):
    """User with this email already exists"""

    pass


async def create_user(
    session: AsyncSession,
    user_info: CreateUserSchema,
) -> UserModel:
    user_info_dict = user_info.model_dump()
    if not user_info_dict.get("username"):
        user_info_dict["username"] = user_info_dict["email"].split("@")[0]
    new_user = UserModel(**user_info_dict)
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailExists
    await session.refresh(new_user)
    return new_user


async def get_users(
    session: AsyncSession,
) -> Sequence[UserModel]:
    query = select(UserModel)
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_by_email(
    session: AsyncSession, email: str, with_profile: bool = False
) -> UserModel | None:
    query = select(UserModel).filter(UserModel.email == email)
    if with_profile:
        query = query.options(joinedload(UserModel.profile))
    result = await session.execute(query)
    return result.scalars().first()
