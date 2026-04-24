import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, AsyncGenerator, BinaryIO, Callable, Coroutine

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


CHUNK_SIZE = 1024 * 1024


def _parse_s3_exception(e: Exception) -> Exception:
    if isinstance(e, ClientError):
        error_code = e.response["Error"]["Code"]  # type: ignore
        match error_code:
            case "NoSuchBucket":
                return NoSuchBucket()
            case "NoSuchKey":
                return NoSuchResume()
            case _:
                return StorageError()
    if isinstance(e, (BotoCoreError, asyncio.TimeoutError)):
        return StorageUnavailable()
    return e


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
    def _handle_s3_exceptions[T, **P](func: Callable[..., Coroutine[Any, Any, T]]):
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise _parse_s3_exception(e)

        return wrapper

    @staticmethod
    def _handle_s3_stream_exceptions(func: Callable[..., AsyncGenerator[bytes, None]]):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                async for chunk in func(self, *args, **kwargs):
                    yield chunk
            except Exception as e:
                raise _parse_s3_exception(e)

        return wrapper

    @_handle_s3_exceptions
    async def put_resume_pdf(self, data: bytes | BinaryIO, object_name: str) -> None:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                ContentType="application/pdf",
            )

    @_handle_s3_exceptions
    async def get_resume_pdf(self, object_name: str) -> bytes:
        async with self.get_client() as client:
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            async with response["Body"] as stream:
                return await stream.read()

    @_handle_s3_stream_exceptions
    async def get_resume_pdf_stream(
        self, object_name: str
    ) -> AsyncGenerator[bytes, None]:
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)

            async with response["Body"] as stream:
                async for chunk in stream.content.iter_chunked(CHUNK_SIZE):
                    yield chunk

    @_handle_s3_exceptions
    async def delete_resume_pdf(self, object_name: str) -> None:
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
