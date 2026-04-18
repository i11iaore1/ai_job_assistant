from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.exc import IntegrityError

from dependencies.auth import (
    AccessUserDependency,
    RefreshIdDependency,
    RefreshInfoDependency,
)
from sa.database import AsyncSessionDependency
from sa.operations.users import (
    create_user,
    create_user_profile,
    delete_all_user_refresh_tokens,
    delete_refresh_token,
    get_user_by_email,
    record_refresh_token,
)
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    FullUserInfoSchema,
    LoginSerializer,
    RegistrationSerializer,
    UserDBSchema,
    UserProfileDBSchema,
)
from utils.security.auth import (
    delete_token_cookies,
    generate_token_pair,
    set_token_cookies,
)

router = APIRouter()


@router.post("/register", response_model=UserDBSchema)
async def register(
    payload: RegistrationSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> UserDBSchema:
    user_info = CreateUserSchema(**payload.model_dump())
    try:
        new_user = await create_user(session=session, user_info=user_info)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )
    new_user_dto = UserDBSchema.model_validate(new_user, from_attributes=True)
    token_pair = generate_token_pair(user=new_user_dto, persistant=payload.remember_me)
    try:
        await record_refresh_token(session=session, token_info=token_pair.refresh.data)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Conflict during refresh-token creation"
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
    user = await get_user_by_email(
        session=session, email=payload.email, with_profile=True
    )
    if user is None or not user.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    user_dto = FullUserInfoSchema.model_validate(user, from_attributes=True)
    token_pair = generate_token_pair(user=user_dto, persistant=payload.remember_me)
    try:
        await record_refresh_token(session=session, token_info=token_pair.refresh.data)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Conflict during refresh-token creation"
        )
    await session.commit()
    set_token_cookies(token_pair=token_pair, response=response)
    return user_dto


@router.post("/logout")
async def logout(
    response: Response, session: AsyncSessionDependency, refresh_id: RefreshIdDependency
):
    if refresh_id:
        await delete_refresh_token(session=session, token_id=refresh_id)
        await session.commit()
    delete_token_cookies(response)
    return {"message": "Logged out"}


@router.post("/refresh")
async def refresh(
    response: Response,
    session: AsyncSessionDependency,
    refresh_info: RefreshInfoDependency,
):
    was_deleted = await delete_refresh_token(
        session=session, token_id=refresh_info.token_info.id
    )
    if not was_deleted:
        await delete_all_user_refresh_tokens(
            session=session, user_id=refresh_info.current_user.id
        )
        await session.commit()
        delete_token_cookies(response)
        raise HTTPException(
            status_code=401, detail="Security alert: Token reuse detected"
        )
    user_dto = UserDBSchema.model_validate(
        refresh_info.current_user, from_attributes=True
    )
    token_pair = generate_token_pair(
        user=user_dto, persistant=refresh_info.token_info.persistant
    )
    try:
        await record_refresh_token(session=session, token_info=token_pair.refresh.data)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Conflict during refresh-token creation"
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
    if current_user.profile:
        raise HTTPException(status_code=409, detail="User already has a profile")
    try:
        new_profile = await create_user_profile(
            session=session, user_id=current_user.id, profile_info=payload
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Conflict during profile creation")
    new_profile_dto = UserProfileDBSchema.model_validate(
        new_profile, from_attributes=True
    )
    return new_profile_dto
