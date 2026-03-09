from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


def createAsyncSessionMaker(asyncEngine: AsyncEngine):
    return async_sessionmaker(bind=asyncEngine, expire_on_commit=True)


async def createAsyncSession(asyncSessionMaker: async_sessionmaker):
    async with asyncSessionMaker() as asyncSession:
        yield asyncSession
