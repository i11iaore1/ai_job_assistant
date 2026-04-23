import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Coroutine

from aiobotocore.session import get_session
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel
from types_aiobotocore_s3.client import S3Client

from exceptions.s3_service import (
    NoSuchBucket,
    NoSuchResume,
    StorageError,
    StorageUnavailable,
)


class AIOBotocoreConfig(BaseModel):
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str


class AppS3Client:
    def __init__(
        self,
        config_model: AIOBotocoreConfig,
        bucket_name: str,
    ) -> None:
        self.client_kwargs = {
            **config_model.model_dump(),
            "config": Config(
                retries={"max_attempts": 3, "mode": "standard"}, region_name="us-east-1"
            ),
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[S3Client, None]:
        async with self.session.create_client("s3", **self.client_kwargs) as client:
            yield client

    @staticmethod
    def handle_s3_errors(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]  # type: ignore
                match error_code:
                    case "NoSuchBucket":
                        raise NoSuchBucket()
                    case "NoSuchKey":
                        raise NoSuchResume()
                    case _:
                        raise StorageError()
            except (BotoCoreError, asyncio.TimeoutError):
                raise StorageUnavailable()

        return wrapper

    @handle_s3_errors
    async def put_resume_pdf(self, data: bytes, object_name: str) -> None:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                ContentType="application/pdf",
            )

    @handle_s3_errors
    async def get_resume_pdf(self, object_name: str) -> bytes:
        async with self.get_client() as client:
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            async with response["Body"] as stream:
                return await stream.read()

    @handle_s3_errors
    async def delete_resume_pdf(self, object_name: str) -> None:
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
