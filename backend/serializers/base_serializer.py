from datetime import datetime

from pydantic import BaseModel


class BaseDatedSerializer(BaseModel):
    created_at: datetime
    updated_at: datetime
