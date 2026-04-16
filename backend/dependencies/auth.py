from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from jwt import ExpiredSignatureError, PyJWTError

from sa_service.database import AsyncSessionDependency
from sa_service.models.users import UserModel
from sa_service.operations.users import get_user_by_id
from serializers.users import FullUserInfoSchema, UserDBSchema
from utils.jwt_service import jwt_decode
from utils.security.auth import (
    PayloadKeys,
    TokenConfig,
    access_token_config,
    refresh_token_config,
)


class TokenPayloadGetter:
    def __init__(self, token_config: TokenConfig):
        self.token_config = token_config

    def __call__(self, request: Request) -> dict[str, Any]:
        token = request.cookies.get(self.token_config.cookie_attrs.key)
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            payload = jwt_decode(token)
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except PyJWTError:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

        if payload.get(PayloadKeys.TYPE) != self.token_config.type_label:
            raise HTTPException(status_code=401, detail="Token type mismatch")

        return payload


get_access_token_payload = TokenPayloadGetter(access_token_config)
get_refresh_token_payload = TokenPayloadGetter(refresh_token_config)


async def get_user_db_record_from_token(
    session: AsyncSessionDependency, payload: dict[str, Any], with_profile: bool
) -> UserModel:
    user_id = payload.get(PayloadKeys.SUBJECT)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User not provided")

    current_user = await get_user_by_id(
        session=session, user_id=int(user_id), with_profile=with_profile
    )
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return current_user


async def get_user_from_access_token(
    session: AsyncSessionDependency,
    payload: dict[str, Any] = Depends(get_access_token_payload),
) -> FullUserInfoSchema:
    current_user = await get_user_db_record_from_token(
        session=session, payload=payload, with_profile=True
    )
    return FullUserInfoSchema.model_validate(current_user, from_attributes=True)


async def get_admin_from_access_token(
    current_user: FullUserInfoSchema = Depends(get_user_from_access_token),
) -> FullUserInfoSchema:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_user_from_refresh_token(
    session: AsyncSessionDependency,
    payload: dict[str, Any] = Depends(get_refresh_token_payload),
) -> UserDBSchema:
    current_user = await get_user_db_record_from_token(
        session=session, payload=payload, with_profile=False
    )
    return UserDBSchema.model_validate(current_user, from_attributes=True)


AccessUserDependency = Annotated[
    FullUserInfoSchema, Depends(get_user_from_access_token)
]
AccessAdminDependency = Annotated[
    FullUserInfoSchema, Depends(get_admin_from_access_token)
]
RefreshUserDependency = Annotated[UserDBSchema, Depends(get_user_from_refresh_token)]
