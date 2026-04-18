from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.user_service import EmailConflict, ProfileConflict, WrongCredentials
from sa.models.users import UserModel, UserProfileModel
from sa.operations.users import (
    create_user,
    create_user_profile,
    delete_refresh_token,
    get_user_by_email,
)
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    FullUserInfoSchema,
    LoginSerializer,
)


async def register_new_user(
    session: AsyncSession, user_info: CreateUserSchema
) -> UserModel:
    if not user_info.username:
        username = user_info.email.split("@")[0]
        user_info = user_info.model_copy(update={"username": username})
    try:
        new_user = await create_user(session=session, user_info=user_info)
    except IntegrityError:
        raise EmailConflict()
    return new_user


async def login_user(session: AsyncSession, payload: LoginSerializer) -> UserModel:
    user = await get_user_by_email(
        session=session, email=payload.email, with_profile=True
    )
    if user is None or not user.verify_password(payload.password):
        raise WrongCredentials()
    return user


async def logout_user(session: AsyncSession, refresh_id: UUID | None) -> bool:
    if refresh_id is None:
        return False
    await delete_refresh_token(session=session, token_id=refresh_id)
    return True


async def create_profile_if_not_exist(
    session: AsyncSession,
    current_user: FullUserInfoSchema,
    profile_info: CreateUserProfileSchema,
) -> UserProfileModel:
    if current_user.profile:
        raise ProfileConflict()
    try:
        new_profile = await create_user_profile(
            session=session, user_id=current_user.id, profile_info=profile_info
        )
    except IntegrityError:
        raise ProfileConflict()
    return new_profile
