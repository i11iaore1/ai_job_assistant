from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from services.s3_service.base import AIOBotocoreConfig


class MinioConfig(BaseSettings):
    root_user: str = Field(validation_alias="MINIO_ROOT_USER")
    root_password: SecretStr = Field(validation_alias="MINIO_ROOT_PASSWORD")
    host: str = Field(validation_alias="MINIO_HOST")
    port: int = Field(validation_alias="MINIO_API_PORT")
    bucket: str = Field(validation_alias="MINIO_BUCKET")

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def aiobotocore_config(self) -> AIOBotocoreConfig:
        return AIOBotocoreConfig(
            endpoint_url=f"{self.host}:{self.port}",
            aws_access_key_id=self.root_user,
            aws_secret_access_key=self.root_password.get_secret_value(),
        )


minio_config = MinioConfig()  # type: ignore
