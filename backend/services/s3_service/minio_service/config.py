from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioConfig(BaseSettings):
    root_user: str = Field(validation_alias="MINIO_ROOT_USER")
    root_password: SecretStr = Field(validation_alias="MINIO_ROOT_PASSWORD")
    host: str = Field(validation_alias="MINIO_HOST", default="localhost")
    port: int = Field(validation_alias="MINIO_API_PORT")
    bucket: str = Field(validation_alias="MINIO_BUCKET")

    model_config = SettingsConfigDict(
        env_file=(".env", "env/minio.env", "env/app.env"), extra="ignore"
    )

    @property
    def aiobotocore_config(self):
        return {
            "endpoint_url": f"{self.host}:{self.port}",
            "aws_access_key_id": self.root_user,
            "aws_secret_access_key": self.root_password.get_secret_value(),
        }


minio_config = MinioConfig()  # type: ignore
