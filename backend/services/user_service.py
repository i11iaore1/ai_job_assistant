from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.user_service import EmailConflict, ProfileConflict, WrongCredentials
from sa.models.users import UserModel, UserProfileModel
from sa.operations.users import (
    create_user,
    create_user_profile,
    get_user_by_email,
)
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    LoginSerializer,
    RegistrationSerializer,
)


async def register_new_user(
    session: AsyncSession,
    user_input: RegistrationSerializer,
    is_admin: bool = False,
) -> UserModel:
    if not user_input.username:
        username = user_input.email.split("@")[0]
        user_input = user_input.model_copy(update={"username": username})
    try:
        user_info = CreateUserSchema(**user_input.model_dump(), is_admin=is_admin)
        new_user = await create_user(session=session, user_info=user_info)
    except IntegrityError:
        raise EmailConflict()
    return new_user


async def login_user(session: AsyncSession, payload: LoginSerializer) -> UserModel:
    user = await get_user_by_email(
        session=session,
        email=payload.email,
        with_profile=True,
    )
    if user is None or not user.verify_password(payload.password):
        raise WrongCredentials()
    return user


async def create_profile_if_not_exist(
    session: AsyncSession,
    current_user: UserModel,
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
