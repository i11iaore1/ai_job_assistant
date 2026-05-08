from fastapi import APIRouter, Form, Response
from fastapi.responses import StreamingResponse

from dependencies.auth import (
    AccessDep,
    OptionalRefreshDep,
    RefreshDep,
    UserFromAccessDep,
    UserFromRefreshDep,
)
from dependencies.file_validation import (
    OptionalResumeFileDependency,
    ResumeFileDependency,
)
from exceptions.jwt_service import TokenReuse
from sa.database import AsyncSessionDependency
from sa.operations.refresh_tokens import delete_all_user_refresh_tokens
from serializers.response import StatusResponse
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
from services.user_service import (
    create_profile_if_not_exist,
    delete_profile,
    delete_user,
    get_profile_if_exists,
    get_resume_file,
    login_user,
    logout_user,
    register_new_user,
    update_profile,
    update_user,
)

router = APIRouter()


@router.post("/register", response_model=UserDBSchema, status_code=201)
async def register(
    payload: RegistrationSerializer,
    session: AsyncSessionDependency,
    response: Response,
):
    new_user = await register_new_user(session=session, user_input=payload)
    new_user_dto = UserDBSchema.model_validate(new_user)
    token_pair = await generate_token_pair(
        session=session,
        user=new_user_dto,
        persistant=payload.remember_me,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return new_user_dto


@router.post("/login", response_model=FullUserInfoSchema, status_code=200)
async def login(
    payload: LoginSerializer,
    session: AsyncSessionDependency,
    response: Response,
):
    user = await login_user(session=session, payload=payload)
    user_dto = FullUserInfoSchema.model_validate(user)
    token_pair = await generate_token_pair(
        session=session,
        user=user_dto,
        persistant=payload.remember_me,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return user_dto


@router.post("/auth/logout", status_code=200)
async def logout(
    response: Response,
    refresh: OptionalRefreshDep,
    session: AsyncSessionDependency,
):
    if refresh is not None:
        await logout_user(session=session, refresh=refresh)
        await session.commit()
    delete_token_cookies(response)
    return StatusResponse(message="Logged out")


@router.post("/auth/refresh", status_code=200)
async def refresh(
    response: Response,
    refresh: RefreshDep,
    current_user: UserFromRefreshDep,
    session: AsyncSessionDependency,
):
    try:
        await delete_previous_refresh_token(
            session=session,
            token=refresh,
        )
    except TokenReuse:
        await delete_all_user_refresh_tokens(session=session, user_id=current_user.id)
        await session.commit()
        raise
    user_dto = UserDBSchema.model_validate(current_user)
    token_pair = await generate_token_pair(
        session=session,
        user=user_dto,
        persistant=refresh.is_persistant,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return StatusResponse(message="Refreshed")



@router.get("/me", response_model=FullUserInfoSchema)
def get_full_user_info(current_user: UserFromAccessDep):
    return current_user


@router.patch("/me", response_model=UserDBSchema)
async def update_current_user(
    payload: UpdateUserSchema,
    access: AccessDep,
    session: AsyncSessionDependency,
):
    updated_user = await update_user(
        user_id=access.subject,
        data_to_update=payload.model_dump(exclude_unset=True),
        session=session,
    )
    await session.commit()
    return updated_user


@router.delete("/me", status_code=204)
async def delete_current_user(
    current_user: UserFromAccessDep,
    session: AsyncSessionDependency,
):
    await delete_user(user=current_user, session=session)
    await session.commit()
    return None


@router.post("/profile", response_model=UserProfileDBSchema, status_code=201)
async def create_profile(
    resume_file: ResumeFileDependency,
    access_token_payload: AccessDep,
    session: AsyncSessionDependency,
    context: str = Form(...),
):
    file_bytes = await resume_file.read()

    new_profile = await create_profile_if_not_exist(
        session=session,
        user_id=access_token_payload.subject,
        file_bytes=file_bytes,
        context=context,
    )

    await session.commit()
    return new_profile


@router.get("/profile", response_model=UserProfileDBSchema)
async def get_profile(
    access_token_payload: AccessDep,
    session: AsyncSessionDependency,
):
    profile = await get_profile_if_exists(
        session=session, user_id=access_token_payload.subject
    )
    return profile


@router.get("/resume-file", response_class=StreamingResponse)
async def get_file(
    resume_file_path: str,
    access_token_payload: AccessDep,
    session: AsyncSessionDependency,
):
    file_stream, metadata = await get_resume_file(
        resume_file_path=resume_file_path,
        is_admin=access_token_payload.is_admin,
        user_id=access_token_payload.subject,
        session=session,
    )

    return StreamingResponse(
        content=file_stream,
        media_type=metadata.content_type,
        headers={
            "Content-Disposition": "inline; filename=resume.pdf",
            "Content-Length": str(metadata.content_length),
        },
    )


@router.patch("/profile", response_model=UserProfileDBSchema)
async def update_user_profile(
    access: AccessDep,
    resume_file: OptionalResumeFileDependency,
    session: AsyncSessionDependency,
    context: str | None = Form(None),
):
    updated_profile = await update_profile(
        session=session,
        user_id=access.subject,
        resume_file=resume_file,
        context=context,
    )

    await session.commit()
    return updated_profile


@router.delete("/profile", status_code=204)
async def delete_user_profile(
    session: AsyncSessionDependency,
    access: AccessDep,
):
    await delete_profile(user_id=access.subject, session=session)
    await session.commit()
    return None
