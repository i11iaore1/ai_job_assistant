from fastapi import APIRouter, Response

from dependencies.auth import (
    FullUserFromAccessDependency,
    RefreshIdDependency,
    RefreshTokenPayloadDependency,
    UserFromAccessDependency,
    UserFromRefreshDependency,
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
    CreateUserProfileSchema,
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
    login_user,
    register_new_user,
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
    updated_user = await update_user(
        session=session,
        user=current_user,
        info_to_update=payload,
    )
    return UserDBSchema.model_validate(updated_user, from_attributes=True)


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
    payload: CreateUserProfileSchema,
    session: AsyncSessionDependency,
    current_user: FullUserFromAccessDependency,
) -> UserProfileDBSchema:
    new_profile = await create_profile_if_not_exist(
        session=session,
        current_user=current_user,
        profile_info=payload,
    )
    new_profile_dto = UserProfileDBSchema.model_validate(
        new_profile, from_attributes=True
    )
    return new_profile_dto
