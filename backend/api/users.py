from fastapi import APIRouter, Form, Response
from fastapi.responses import StreamingResponse

from dependencies.auth import (
    AccessTokenPayloadDependency,
    FullUserFromAccessDependency,
    RefreshIdDependency,
    RefreshTokenPayloadDependency,
    UserFromAccessDependency,
    UserFromRefreshDependency,
)
from dependencies.file_validation import (
    OptionalResumeFileDependency,
    ResumeFileDependency,
)
from exceptions.jwt_service import TokenReuse
from sa.database import AsyncSessionDependency
from sa.operations.users import (
    delete_all_user_refresh_tokens,
    delete_refresh_token,
    delete_user,
    update_user,
)
from serializers.users import (
    FullUserInfoSchema,
    LoginSerializer,
    RegistrationSerializer,
    UpdateUserSchema,
    UserDBSchema,
    UserProfileDBSchema,
)
from services.jwt_service import (
    delete_previous_refresh_token,
    delete_token_cookies,
    generate_token_pair,
    set_token_cookies,
)
from services.s3_service import s3_client
from services.user_service import (
    check_permission_for_resume,
    create_profile_if_not_exist,
    get_profile_if_exists,
    login_user,
    register_new_user,
    update_profile,
)

router = APIRouter()


@router.post("/register", response_model=UserDBSchema)
async def register(
    payload: RegistrationSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> UserDBSchema:
    new_user = await register_new_user(session=session, user_input=payload)
    new_user_dto = UserDBSchema.model_validate(new_user, from_attributes=True)
    token_pair = await generate_token_pair(
        session=session,
        user=new_user_dto,
        persistant=payload.remember_me,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return new_user_dto


@router.post("/login", response_model=FullUserInfoSchema)
async def login(
    payload: LoginSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> FullUserInfoSchema:
    user = await login_user(session=session, payload=payload)
    user_dto = FullUserInfoSchema.model_validate(user, from_attributes=True)
    token_pair = await generate_token_pair(
        session=session,
        user=user_dto,
        persistant=payload.remember_me,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return user_dto


@router.get("/me")
def get_full_user_info(
    current_user: FullUserFromAccessDependency,
) -> FullUserInfoSchema:
    return FullUserInfoSchema.model_validate(current_user, from_attributes=True)


@router.patch("/me")
async def update_user_account(
    session: AsyncSessionDependency,
    current_user: UserFromAccessDependency,
    payload: UpdateUserSchema,
) -> UserDBSchema:
    await update_user(
        session=session,
        user=current_user,
        info_to_update=payload,
    )
    return UserDBSchema.model_validate(current_user, from_attributes=True)


@router.delete("/me")
async def delete_user_account(
    session: AsyncSessionDependency,
    current_user: UserFromAccessDependency,
    response: Response,
):
    await delete_user(session=session, user=current_user)
    await session.commit()
    response.status_code = 204


@router.post("/auth/logout")
async def logout(
    session: AsyncSessionDependency,
    refresh_id: RefreshIdDependency,
    response: Response,
):
    if refresh_id is not None:
        await delete_refresh_token(session=session, token_id=refresh_id)
        await session.commit()
    delete_token_cookies(response)
    return {"message": "Logged out"}


@router.post("/auth/refresh")
async def refresh(
    session: AsyncSessionDependency,
    refresh_payload: RefreshTokenPayloadDependency,
    current_user: UserFromRefreshDependency,
    response: Response,
):
    try:
        await delete_previous_refresh_token(
            session=session,
            token_id=refresh_payload.jwt_id,
        )
    except TokenReuse:
        await delete_all_user_refresh_tokens(session=session, user_id=current_user.id)
        await session.commit()
        raise
    user_dto = UserDBSchema.model_validate(current_user, from_attributes=True)
    token_pair = await generate_token_pair(
        session=session,
        user=user_dto,
        persistant=refresh_payload.is_persistant,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return {"message": "Refreshed"}


@router.post("/profile", response_model=UserProfileDBSchema)
async def create_profile(
    session: AsyncSessionDependency,
    access_token_payload: AccessTokenPayloadDependency,
    resume_file: ResumeFileDependency,
    context: str = Form(...),
) -> UserProfileDBSchema:
    file_bytes = await resume_file.read()

    new_profile = await create_profile_if_not_exist(
        session=session,
        user_id=access_token_payload.subject,
        file_bytes=file_bytes,
        context=context,
    )
    await s3_client.put_resume_pdf(
        data=file_bytes, object_name=new_profile.resume_file_path
    )

    await session.commit()
    return UserProfileDBSchema.model_validate(new_profile, from_attributes=True)


@router.get("/profile", response_model=UserProfileDBSchema)
async def get_profile(
    session: AsyncSessionDependency,
    access_token_payload: AccessTokenPayloadDependency,
) -> UserProfileDBSchema:
    profile = await get_profile_if_exists(
        session=session, user_id=access_token_payload.subject
    )
    return UserProfileDBSchema.model_validate(profile, from_attributes=True)


@router.get("/resume-file", response_class=StreamingResponse)
async def get_file(
    resume_file_path: str,
    session: AsyncSessionDependency,
    access_token_payload: AccessTokenPayloadDependency,
) -> Response:
    await check_permission_for_resume(
        resume_file_path=resume_file_path,
        is_admin=access_token_payload.is_admin,
        user_id=access_token_payload.subject,
        session=session,
    )

    file_stream = s3_client.get_resume_pdf_stream(resume_file_path)

    return StreamingResponse(
        content=file_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=resume.pdf"},
    )


@router.patch("/profile", response_model=UserProfileDBSchema)
async def update_user_profile(
    session: AsyncSessionDependency,
    current_user: FullUserFromAccessDependency,
    resume_file: OptionalResumeFileDependency,
    context: str | None = Form(None),
) -> UserProfileDBSchema:
    await update_profile(
        session=session,
        profile=current_user.profile,
        resume_file=resume_file,
        context=context,
    )

    await session.commit()
    return UserProfileDBSchema.model_validate(
        current_user.profile, from_attributes=True
    )
