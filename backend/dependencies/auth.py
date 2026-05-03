from functools import wraps
from typing import Annotated, Awaitable, Callable
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import APIKeyCookie
from jwt import ExpiredSignatureError, PyJWTError
from pydantic import ValidationError

from exceptions.jwt_service import (
    NotAuthenticated,
    TokenExpired,
    TokenInvalid,
    TokenTypeMismatch,
)
from exceptions.user_service import UserNotFound
from sa.database import AsyncSessionDependency
from sa.models.users import UserModel
from sa.repositories import user_repository
from utils.jwt_service import jwt_decode
from utils.security.auth import (
    AccessTokenPayloadSchema,
    RefreshTokenPayloadSchema,
    TokenConfig,
    TokenPayloadSchema,
    access_token_config,
    refresh_token_config,
)


def token_payload_dependency_factory[T: TokenPayloadSchema](
    token_config: TokenConfig[T],
):
    def extract_and_validate_payload(
        request: Request,
        _=Depends(
            APIKeyCookie(
                name=token_config.default_cookie_attrs.key,
                scheme_name=f"{token_config.type_label.capitalize()} Cookie",
                auto_error=False,
            )
        ),
    ) -> T:
        token_str = request.cookies.get(token_config.default_cookie_attrs.key)
        if token_str is None:
            raise NotAuthenticated()
        try:
            raw_payload_dict = jwt_decode(token_str)
        except ExpiredSignatureError:
            raise TokenExpired()
        except PyJWTError:
            raise TokenInvalid()
        try:
            validated_payload = token_config.payload_validation_model.model_validate(
                raw_payload_dict
            )
        except ValidationError:
            raise TokenInvalid()

        if validated_payload.type != token_config.type_label:
            raise TokenTypeMismatch()

        return validated_payload

    return extract_and_validate_payload


AccessTokenPayloadDependency = Annotated[
    AccessTokenPayloadSchema,
    Depends(token_payload_dependency_factory(access_token_config)),
]
RefreshTokenPayloadDependency = Annotated[
    RefreshTokenPayloadSchema,
    Depends(token_payload_dependency_factory(refresh_token_config)),
]


def raise_not_found[**P](
    user_getter: Callable[P, Awaitable[UserModel | None]],
) -> Callable[P, Awaitable[UserModel]]:
    @wraps(user_getter)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> UserModel:
        user = await user_getter(*args, **kwargs)
        if user is None:
            raise UserNotFound()
        return user

    return wrapper


@raise_not_found
async def get_user_from_access_token(
    session: AsyncSessionDependency,
    payload: AccessTokenPayloadDependency,
) -> UserModel | None:
    return await user_repository.get_by_id(
        id=payload.subject,
        session=session,
    )


@raise_not_found
async def get_user_with_profile_from_access_token(
    session: AsyncSessionDependency,
    payload: AccessTokenPayloadDependency,
) -> UserModel | None:
    return await user_repository.get_by_id_with_profile(
        id=payload.subject,
        session=session,
    )


@raise_not_found
async def get_user_from_refresh_token(
    session: AsyncSessionDependency,
    payload: RefreshTokenPayloadDependency,
) -> UserModel | None:
    return await user_repository.get_by_id(
        id=payload.subject,
        session=session,
    )


@raise_not_found
async def get_user_with_profile_from_refresh_token(
    session: AsyncSessionDependency,
    payload: RefreshTokenPayloadDependency,
) -> UserModel | None:
    return await user_repository.get_by_id_with_profile(
        id=payload.subject,
        session=session,
    )


# async def get_admin_from_access_token(
#     current_user: FullUserInfoSchema = Depends(get_user_with_profile_from_access_token),
# ) -> FullUserInfoSchema:
#     if not current_user.is_admin:
#         raise NotAdmin()
#     return current_user


def get_refresh_id_if_exists(request: Request) -> UUID | None:
    try:
        token = request.cookies.get(refresh_token_config.default_cookie_attrs.key)
        if token is None:
            return None
        payload_dict = jwt_decode(token, verify_exp=False)
        payload_dto = RefreshTokenPayloadSchema.model_validate(payload_dict)
        return payload_dto.jwt_id
    except (ValueError, PyJWTError, ValidationError):
        # if token is absent or invalid, cookies still should be deleted
        return None


UserFromAccessDependency = Annotated[UserModel, Depends(get_user_from_access_token)]
FullUserFromAccessDependency = Annotated[
    UserModel, Depends(get_user_with_profile_from_access_token)
]
UserFromRefreshDependency = Annotated[UserModel, Depends(get_user_from_refresh_token)]

RefreshIdDependency = Annotated[UUID | None, Depends(get_refresh_id_if_exists)]
