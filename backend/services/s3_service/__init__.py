from .base import AppS3Client
from .minio_service.config import minio_config

s3_client = AppS3Client(
    config_model=minio_config.aiobotocore_config,
    bucket_name=minio_config.bucket,
    stream_chunk_size=minio_config.stream_chunk_size,
)

__all__ = ["s3_client"]
