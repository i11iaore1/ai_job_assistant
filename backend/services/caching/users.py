from typing import assert_never

from sa.models import UserModel
from serializers.users import FullUserInfoSchema
from services.caching.protocol import AsyncCachingClient
from services.caching.redis_service.client import redis_client


class UserCaching:
    def __init__(self, client: AsyncCachingClient) -> None:
        self.client = client

    @staticmethod
    def get_key(user_id: int) -> str:
        return f"user-{user_id}"

    async def add(
        self,
        user_id: int,
        user: FullUserInfoSchema | UserModel | None,
    ) -> None:
        if user is None:
            await self.client.set(
                key=self.get_key(user_id),
                value="",
                expiration=300,
            )
            return
        elif isinstance(user, FullUserInfoSchema):
            value = user.model_dump_json()
        elif isinstance(user, UserModel):
            value = FullUserInfoSchema.model_validate(user).model_dump_json()
        else:
            assert_never(user)

        await self.client.set(
            key=self.get_key(user.id),
            value=value,
        )

    async def get(self, user_id: int) -> FullUserInfoSchema | None:
        value = await self.client.get(self.get_key(user_id))
        if value is not None:
            return FullUserInfoSchema.model_validate_json(value)

    async def remove(self, user_id: int) -> None:
        await self.client.delete(self.get_key(user_id))


user_caching = UserCaching(redis_client)
