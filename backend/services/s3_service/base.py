import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, AsyncGenerator, BinaryIO, Callable, Coroutine

from aiobotocore.session import get_session
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from types_aiobotocore_s3.client import S3Client

from exceptions.s3_service import (
    NoSuchBucket,
    NoSuchFile,
    StorageError,
    StorageUnavailable,
)
from services.s3_service.models import AIOBotocoreConfig, FileMetadata


def _map_s3_exception(e: Exception) -> Exception:
    if isinstance(e, ClientError):
        error_code = e.response["Error"]["Code"]  # type: ignore
        match error_code:
            case "NoSuchBucket":
                return NoSuchBucket()
            case "NoSuchKey":
                return NoSuchFile()
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
        stream_chunk_size: int,
    ) -> None:
        self.client_kwargs = {
            **config_model.model_dump(),
            "config": Config(
                retries={"max_attempts": 3, "mode": "standard"}, region_name="us-east-1"
            ),
        }
        self.bucket_name = bucket_name
        self.stream_chunk_size = stream_chunk_size
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
                raise _map_s3_exception(e)

        return wrapper

    @staticmethod
    def _handle_s3_stream_exceptions(func: Callable[..., AsyncGenerator[bytes, None]]):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                async for chunk in func(self, *args, **kwargs):
                    yield chunk
            except Exception as e:
                raise _map_s3_exception(e)

        return wrapper

    @_handle_s3_exceptions
    async def put_file(
        self,
        data: bytes | BinaryIO,
        object_name: str,
        content_type: str = "application/pdf",
    ) -> None:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                ContentType=content_type,
            )

    @_handle_s3_exceptions
    async def get_file_metadata(self, object_name: str) -> FileMetadata:
        async with self.get_client() as client:
            response = await client.head_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            metadata = FileMetadata(
                content_length=response.get("ContentLength"),
                content_type=response.get("ContentType"),
                last_modified=response.get("LastModified"),
            )
            return metadata

    @_handle_s3_exceptions
    async def get_file(self, object_name: str) -> bytes:
        async with self.get_client() as client:
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
            async with response["Body"] as stream:
                return await stream.read()

    @_handle_s3_stream_exceptions
    async def get_file_stream(self, object_name: str) -> AsyncGenerator[bytes, None]:
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)

            async with response["Body"] as stream:
                async for chunk in stream.content.iter_chunked(self.stream_chunk_size):
                    yield chunk

    @_handle_s3_exceptions
    async def delete_file(self, object_name: str) -> None:
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name,
            )
