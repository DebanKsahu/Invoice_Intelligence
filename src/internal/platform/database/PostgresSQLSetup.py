from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from internal.platform.config.Settings import Settings
from internal.platform.database.models.UserInDatabase import UserInDatabase


def createAsyncEngine(settings: Settings):
    return create_async_engine(url=settings.databaseSettings.DATABASE_URL, echo=False)


async def initPostgresSQL(asyncEngine: AsyncEngine):
    async with asyncEngine.begin() as engine:
        await engine.run_sync(SQLModel.metadata.create_all)

async def closePostgresSQL(asyncEngine: AsyncEngine):
    await asyncEngine.dispose()
