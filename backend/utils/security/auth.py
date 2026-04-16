from datetime import datetime, timedelta, timezone
from typing import Final, Literal, NamedTuple

from fastapi import Response

from serializers.users import UserDBSchema
from utils.jwt_service import jwt_encode


class CookieAttributes(NamedTuple):
    key: str
    max_age: int | None
    httponly: bool
    samesite: Literal["lax", "strict", "none"]
    secure: bool


class TokenConfig(NamedTuple):
    type_label: str
    exp_seconds: int
    cookie_attrs: CookieAttributes


access_token_config = TokenConfig(
    type_label="access",
    exp_seconds=30 * 60,  # 30 minutes
    cookie_attrs=CookieAttributes(
        key="access",
        max_age=30 * 60,  # 30 minutes
        httponly=True,
        samesite="lax",
        secure=False,
    ),
)

refresh_token_config = TokenConfig(
    type_label="refresh",
    exp_seconds=7 * 24 * 3600,  # 7 days
    cookie_attrs=CookieAttributes(
        key="refresh",
        max_age=7 * 24 * 3600,  # 7 days
        httponly=True,
        samesite="lax",
        secure=False,
    ),
)


class PayloadKeys:
    SUBJECT: Final = "sub"
    TYPE: Final = "typ"
    ADMIN: Final = "adm"
    EXPIRATION: Final = "exp"


class TokenPair(NamedTuple):
    access: str
    refresh: str


def generate_token_pair(user: UserDBSchema) -> TokenPair:
    now = datetime.now(timezone.utc)
    access_exp = now + timedelta(seconds=access_token_config.exp_seconds)
    refresh_exp = now + timedelta(seconds=refresh_token_config.exp_seconds)
    access_payload = {
        PayloadKeys.SUBJECT: str(user.id),
        PayloadKeys.TYPE: access_token_config.type_label,
        PayloadKeys.ADMIN: user.is_admin,
        PayloadKeys.EXPIRATION: access_exp,
    }
    refresh_payload = {
        PayloadKeys.SUBJECT: str(user.id),
        PayloadKeys.TYPE: refresh_token_config.type_label,
        PayloadKeys.EXPIRATION: refresh_exp,
    }
    return TokenPair(
        access=jwt_encode(access_payload), refresh=jwt_encode(refresh_payload)
    )


def set_token_cookies(user: UserDBSchema, response: Response, remember_me: bool):
    token_pair = generate_token_pair(user)
    response.set_cookie(
        **access_token_config.cookie_attrs._asdict(), value=token_pair.access
    )
    refresh_cookie_attrs = refresh_token_config.cookie_attrs
    if not remember_me:
        # if not remember_me, set max_age to None (session cookie)
        refresh_cookie_attrs = refresh_cookie_attrs._replace(max_age=None)
    response.set_cookie(**refresh_cookie_attrs._asdict(), value=token_pair.refresh)


def delete_token_cookies(response: Response):
    response.delete_cookie(
        key=access_token_config.cookie_attrs.key,
        httponly=access_token_config.cookie_attrs.httponly,
        samesite=access_token_config.cookie_attrs.samesite,
    )
    response.delete_cookie(
        key=refresh_token_config.cookie_attrs.key,
        httponly=refresh_token_config.cookie_attrs.httponly,
        samesite=refresh_token_config.cookie_attrs.samesite,
    )
