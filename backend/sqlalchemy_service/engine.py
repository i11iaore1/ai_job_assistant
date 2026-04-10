from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy_service.config import pg_config


POOL_SIZE = 5
MAX_OVERFLOW = 10


engine = create_engine(
    url=pg_config.DSN_psycopg, echo=True, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW
)

async_engine = create_async_engine(
    url=pg_config.DSN_psycopg, echo=True, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW
)
