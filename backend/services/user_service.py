from typing import AsyncGenerator, NamedTuple
from uuid import uuid4

from fastapi import UploadFile
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
from sa.repositories import user_profile_repository, user_repository
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    LoginSerializer,
    RegistrationSerializer,
    UpdateUserProfileSchema,
)
from services.s3_service import s3_client
from services.s3_service.models import FileMetadata
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
        new_user = await user_repository.create(
            session=session, data=user_info.model_dump()
        )
    except IntegrityError:
        raise EmailConflict()
    return new_user


async def login_user(session: AsyncSession, payload: LoginSerializer) -> UserModel:
    user = await user_repository.get_by_email_with_profile(
        session=session,
        email=payload.email,
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
        data = {"user_id": user_id, **profile_info.model_dump()}
        new_profile = await user_profile_repository.create(data=data, session=session)
    except IntegrityError:
        raise ProfileConflict()

    return new_profile


async def get_profile_if_exists(
    session: AsyncSession, user_id: int
) -> UserProfileModel:
    profile = await user_profile_repository.get_by_id(id=user_id, session=session)
    if profile is None:
        raise NoProfile()
    return profile


class FileWithMetaData(NamedTuple):
    stream: AsyncGenerator[bytes, None]
    metadata: FileMetadata


async def get_resume_file(
    resume_file_path: str,
    is_admin: bool,
    user_id: int,
    session: AsyncSession,
) -> FileWithMetaData:
    if not is_admin:
        profile = await user_profile_repository.get_by_id(id=user_id, session=session)
        if profile is None or not profile.resume_file_path == resume_file_path:
            raise NotResumeOwner()

    return FileWithMetaData(
        stream=s3_client.get_file_stream(resume_file_path),
        metadata=await s3_client.get_file_metadata(resume_file_path),
    )


async def update_profile(
    session: AsyncSession,
    profile: UserProfileModel,
    resume_file: UploadFile | None,
    context: str | None,
) -> None:
    info_to_update = UpdateUserProfileSchema()

    if context is not None:
        info_to_update.context = context

    if resume_file:
        current_object_name = profile.resume_file_path

        file_bytes = await resume_file.read()
        new_object_name = f"{uuid4()}.pdf"
        new_file_text = get_pdf_text_from_stream(file_bytes)

        info_to_update.resume_text = new_file_text
        info_to_update.resume_file_path = new_object_name

    if not info_to_update.model_fields_set:
        return

    data = info_to_update.model_dump(exclude_unset=True)

    await user_profile_repository.update(
        instance=profile,
        data=data,
        session=session,
    )

    if resume_file:
        await s3_client.put_file(data=file_bytes, object_name=profile.resume_file_path)

        await s3_client.delete_file(current_object_name)
