from datetime import datetime
from typing import Final, Literal, NamedTuple
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field

from serializers.users import RefreshTokenSchema, UserDBSchema
from utils.jwt_service import jwt_encode


class TokenPayloadKeys:
    # general
    SUBJECT: Final = "sub"
    TYPE: Final = "typ"
    EXPIRATION: Final = "exp"
    # access
    ADMIN: Final = "adm"
    # refresh
    JWT_ID: Final = "jti"
    PERSISTANT: Final = "pnt"


class AccessTokenPayloadSchema(BaseModel):
    subject: int = Field(serialization_alias=TokenPayloadKeys.SUBJECT)
    type: str = Field(serialization_alias=TokenPayloadKeys.TYPE)
    expiration: datetime = Field(serialization_alias=TokenPayloadKeys.EXPIRATION)
    is_admin: bool = Field(serialization_alias=TokenPayloadKeys.ADMIN)


class RefreshTokenPayloadSchema(BaseModel):
    subject: int = Field(serialization_alias=TokenPayloadKeys.SUBJECT)
    type: str = Field(serialization_alias=TokenPayloadKeys.TYPE)
    expiration: datetime = Field(serialization_alias=TokenPayloadKeys.EXPIRATION)
    jwt_id: UUID4 = Field(serialization_alias=TokenPayloadKeys.JWT_ID)
    is_persistant: bool = Field(serialization_alias=TokenPayloadKeys.PERSISTANT)


TokenPayloadSchema = type[AccessTokenPayloadSchema] | type[RefreshTokenPayloadSchema]


class CookieAttributes(NamedTuple):
    key: str
    max_age: int | None
    httponly: bool
    path: str
    samesite: Literal["lax", "strict", "none"]
    secure: bool


class TokenConfig[T: TokenPayloadSchema](BaseModel):
    type_label: str
    payload_validation_model: T
    exp_seconds: int
    shorter_exp_seconds: int
    default_cookie_attrs: CookieAttributes


access_token_config = TokenConfig(
    type_label="access",
    payload_validation_model=AccessTokenPayloadSchema,
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
    payload_validation_model=RefreshTokenPayloadSchema,
    exp_seconds=7 * 24 * 3600,  # 7 days
    shorter_exp_seconds=3600,  # 1 hour
    default_cookie_attrs=CookieAttributes(
        key="refresh",
        max_age=7 * 24 * 3600,  # 7 days
        httponly=True,
        path="/auth",
        samesite="lax",
        secure=False,
    ),
)


class AccessToken(NamedTuple):
    encoded: str


class RefreshToken(NamedTuple):
    db_data: RefreshTokenSchema
    encoded: str


class TokenPair(NamedTuple):
    access: AccessToken
    refresh: RefreshToken


def generate_access_token(user: UserDBSchema, expiration: datetime) -> AccessToken:
    payload = AccessTokenPayloadSchema(
        subject=user.id,
        type=access_token_config.type_label,
        is_admin=user.is_admin,
        expiration=expiration,
    )

    return AccessToken(encoded=jwt_encode(payload.model_dump(mode="json")))


def generate_refresh_token(
    user: UserDBSchema, expiration: datetime, persistant: bool
) -> RefreshToken:
    jti = uuid4()

    payload = RefreshTokenPayloadSchema(
        subject=user.id,
        type=refresh_token_config.type_label,
        expiration=expiration,
        jwt_id=jti,
        is_persistant=persistant,
    )

    token_dto = RefreshTokenSchema(jti=jti, user_id=user.id, expires_at=expiration)

    return RefreshToken(
        db_data=token_dto,
        encoded=jwt_encode(payload.model_dump(mode="json")),
    )
