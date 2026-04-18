import uuid
from datetime import datetime
from typing import Final, Literal, NamedTuple

from serializers.users import RefreshTokenSchema, UserDBSchema
from utils.jwt_service import jwt_encode


class CookieAttributes(NamedTuple):
    key: str
    max_age: int | None
    httponly: bool
    path: str
    samesite: Literal["lax", "strict", "none"]
    secure: bool


class TokenConfig(NamedTuple):
    type_label: str
    exp_seconds: int
    shorter_exp_seconds: int
    default_cookie_attrs: CookieAttributes


access_token_config = TokenConfig(
    type_label="access",
    exp_seconds=30 * 60,  # 30 minutes
    shorter_exp_seconds=10 * 60,  # 10 minutes
    default_cookie_attrs=CookieAttributes(
        key="access",
        max_age=30 * 60,  # 30 minutes
        httponly=True,
        path="/",
        samesite="lax",
        secure=False,
    ),
)

refresh_token_config = TokenConfig(
    type_label="refresh",
    exp_seconds=7 * 24 * 3600,  # 7 days
    shorter_exp_seconds=3600,  # 1 hour
    default_cookie_attrs=CookieAttributes(
        key="refresh",
        max_age=7 * 24 * 3600,  # 7 days
        httponly=True,
        path="/refresh",
        samesite="lax",
        secure=False,
    ),
)


class PayloadKeys:
    # general
    SUBJECT: Final = "sub"
    TYPE: Final = "typ"
    EXPIRATION: Final = "exp"
    # access
    ADMIN: Final = "adm"
    # refresh
    JWT_ID: Final = "jti"
    PERSISTANT: Final = "pnt"


class AccessToken(NamedTuple):
    encoded: str


class RefreshToken(NamedTuple):
    data: RefreshTokenSchema
    encoded: str


class TokenPair(NamedTuple):
    access: AccessToken
    refresh: RefreshToken


def generate_access_token(user: UserDBSchema, expiration: datetime) -> AccessToken:
    user_id = str(user.id)

    payload = {
        PayloadKeys.SUBJECT: user_id,
        PayloadKeys.TYPE: access_token_config.type_label,
        PayloadKeys.ADMIN: user.is_admin,
        PayloadKeys.EXPIRATION: expiration,
    }
    return AccessToken(encoded=jwt_encode(payload))


def generate_refresh_token(
    user: UserDBSchema, expiration: datetime, persistant: bool
) -> RefreshToken:
    user_id = str(user.id)
    jti = str(uuid.uuid4())

    payload = {
        PayloadKeys.SUBJECT: user_id,
        PayloadKeys.TYPE: refresh_token_config.type_label,
        PayloadKeys.EXPIRATION: expiration,
        PayloadKeys.JWT_ID: jti,
        PayloadKeys.PERSISTANT: persistant,
    }

    token_dto = RefreshTokenSchema(jti=jti, user_id=user_id, expires_at=expiration)

    return RefreshToken(data=token_dto, encoded=jwt_encode(payload))
