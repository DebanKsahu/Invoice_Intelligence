from contextlib import asynccontextmanager
from dataclasses import dataclass
from logging import Logger
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from internal.platform.config.Settings import Settings


@dataclass(frozen=True)
class AppDependency:
    # Config Dependencies
    settings: Settings

    # Database Depedencies
    asyncEngine: AsyncEngine
    asyncSessionMaker: async_sessionmaker

    logger: Logger

    @asynccontextmanager
    async def getAsyncSession(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.asyncSessionMaker() as session:
            yield session
