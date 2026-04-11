from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from sa_service.config import CURRENT_DSN


POOL_SIZE = 5
MAX_OVERFLOW = 10


engine = create_engine(
    url=CURRENT_DSN, echo=True, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW
)

async_engine = create_async_engine(
    url=CURRENT_DSN, echo=True, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW
)
