from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.user_service import (
    EmailConflict,
    NoProfile,
    NotResumeOwner,
    ProfileConflict,
    WrongCredentials,
)
from sa.models.users import UserModel, UserProfileModel
from sa.operations.users import (
    create_user,
    create_user_profile,
    get_profile_by_user_id,
    get_user_by_email,
)
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    LoginSerializer,
    RegistrationSerializer,
)
from utils.pdf_processing import get_pdf_text_from_stream


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
    user_id: int,
    file_bytes: bytes,
    context: str,
) -> UserProfileModel:
    object_name = f"{uuid4()}.pdf"
    file_text = get_pdf_text_from_stream(file_bytes)

    profile_info = CreateUserProfileSchema(
        resume_file_path=object_name,
        resume_text=file_text,
        context=context,
    )

    try:
        new_profile = await create_user_profile(
            session=session,
            user_id=user_id,
            profile_info=profile_info,
        )
    except IntegrityError:
        raise ProfileConflict()

    return new_profile


async def get_profile_if_exists(
    session: AsyncSession, user_id: int
) -> UserProfileModel:
    profile = await get_profile_by_user_id(session=session, user_id=user_id)
    if profile is None:
        raise NoProfile()
    return profile


async def check_permission_for_resume(
    resume_file_path: str,
    is_admin: bool,
    user_id: int,
    session: AsyncSession,
):
    if not is_admin:
        profile = await get_profile_by_user_id(session=session, user_id=user_id)
        if profile is None or not profile.resume_file_path == resume_file_path:
            raise NotResumeOwner()
