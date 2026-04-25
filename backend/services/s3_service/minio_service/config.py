from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from services.s3_service.models import AIOBotocoreConfig


class MinioConfig(BaseSettings):
    root_user: str = Field(validation_alias="MINIO_ROOT_USER")
    root_password: SecretStr = Field(validation_alias="MINIO_ROOT_PASSWORD")
    host: str = Field(validation_alias="MINIO_HOST")
    port: int = Field(validation_alias="MINIO_API_PORT")
    bucket: str = Field(validation_alias="MINIO_BUCKET")
    stream_chunk_size_kb: int = Field(
        validation_alias="MINIO_CHUNK_SIZE_KB",
        default=1024,
    )

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def stream_chunk_size(self) -> int:
        return self.stream_chunk_size_kb * 1024

    @property
    def aiobotocore_config(self) -> AIOBotocoreConfig:
        return AIOBotocoreConfig(
            endpoint_url=f"{self.host}:{self.port}",
            aws_access_key_id=self.root_user,
            aws_secret_access_key=self.root_password.get_secret_value(),
        )


minio_config = MinioConfig()  # type: ignore
