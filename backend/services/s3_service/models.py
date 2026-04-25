from datetime import datetime

from pydantic import BaseModel


class AIOBotocoreConfig(BaseModel):
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str


class FileMetadata(BaseModel):
    content_length: int
    content_type: str
    last_modified: datetime
