from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.jwt_service import TokenReuse
from sa.operations.refresh_tokens import (
    delete_refresh_token,
    record_refresh_token,
)
from serializers.users import UserDBSchema
from utils.security.auth import (
    TokenPair,
    access_token_config,
    generate_access_token,
    generate_refresh_token,
    refresh_token_config,
)


async def generate_token_pair(
    session: AsyncSession, user: UserDBSchema, persistant: bool
) -> TokenPair:
    now = datetime.now(timezone.utc)
    access_exp_seconds = (
        access_token_config.exp_seconds
        if persistant
        else access_token_config.shorter_exp_seconds
    )
    refresh_exp_seconds = (
        refresh_token_config.exp_seconds
        if persistant
        else refresh_token_config.shorter_exp_seconds
    )

    access_exp = now + timedelta(seconds=access_exp_seconds)
    refresh_exp = now + timedelta(seconds=refresh_exp_seconds)

    access_token = generate_access_token(user=user, expiration=access_exp)
    refresh_token = generate_refresh_token(
        user=user, expiration=refresh_exp, persistant=persistant
    )

    await record_refresh_token(session=session, token_info=refresh_token.db_data)

    return TokenPair(access=access_token, refresh=refresh_token)


async def delete_previous_refresh_token(
    session: AsyncSession,
    token_id: UUID,
) -> None:
    was_deleted = await delete_refresh_token(session=session, token_id=token_id)
    if not was_deleted:
        raise TokenReuse()


# cookie management


def set_token_cookies(token_pair: TokenPair, response: Response):
    response.set_cookie(
        **access_token_config.default_cookie_attrs._asdict(),
        value=token_pair.access.encoded,
    )
    response.set_cookie(
        **refresh_token_config.default_cookie_attrs._asdict(),
        value=token_pair.refresh.encoded,
    )


def delete_token_cookies(response: Response):
    for token_config in (access_token_config, refresh_token_config):
        response.delete_cookie(
            key=token_config.default_cookie_attrs.key,
            httponly=token_config.default_cookie_attrs.httponly,
            samesite=token_config.default_cookie_attrs.samesite,
            path=token_config.default_cookie_attrs.path,
        )
