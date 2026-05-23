from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    host: str = Field(validation_alias="REDIS_HOST")
    port: int = Field(validation_alias="REDIS_PORT")

    model_config = SettingsConfigDict(extra="ignore")


redis_config = RedisConfig()  # type: ignore
