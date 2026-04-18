from fastapi import APIRouter, Response

from dependencies.auth import (
    AccessUserDependency,
    RefreshIdDependency,
    RefreshInfoDependency,
)
from exceptions.jwt_service import TokenReuse
from sa.database import AsyncSessionDependency
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    FullUserInfoSchema,
    LoginSerializer,
    RegistrationSerializer,
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
    login_user,
    logout_user,
    register_new_user,
)

router = APIRouter()


@router.post("/register", response_model=UserDBSchema)
async def register(
    payload: RegistrationSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> UserDBSchema:
    user_info = CreateUserSchema(**payload.model_dump())
    new_user = await register_new_user(session=session, user_info=user_info)
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


@router.post("/logout")
async def logout(
    response: Response, session: AsyncSessionDependency, refresh_id: RefreshIdDependency
):
    logged_out = logout_user(session=session, refresh_id=refresh_id)
    if logged_out:
        await session.commit()
    delete_token_cookies(response)
    return {"message": "Logged out"}


@router.post("/refresh")
async def refresh(
    response: Response,
    session: AsyncSessionDependency,
    refresh_info: RefreshInfoDependency,
):
    try:
        await delete_previous_refresh_token(session=session, refresh_info=refresh_info)
    except TokenReuse:
        await session.commit()
        delete_token_cookies(response)
        raise
    user_dto = UserDBSchema.model_validate(
        refresh_info.current_user, from_attributes=True
    )
    token_pair = await generate_token_pair(
        session=session,
        user=user_dto,
        persistant=refresh_info.token_info.persistant,
    )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return {"message": "Refreshed"}


@router.post("/profile", response_model=UserProfileDBSchema)
async def create_profile(
    payload: CreateUserProfileSchema,
    session: AsyncSessionDependency,
    current_user: AccessUserDependency,
):
    new_profile = await create_profile_if_not_exist(
        session=session,
        current_user=current_user,
        profile_info=payload,
    )
    new_profile_dto = UserProfileDBSchema.model_validate(
        new_profile, from_attributes=True
    )
    return new_profile_dto
