from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sa_service.config import CURRENT_DSN

POOL_SIZE = 5
MAX_OVERFLOW = 10


engine = create_engine(
    url=CURRENT_DSN,
    echo=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,
)

async_engine = create_async_engine(
    url=CURRENT_DSN,
    echo=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,
)


SessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False
)


async def get_async_session():
    async with SessionLocal() as session:
        yield session


AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
