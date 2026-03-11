from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.AppDependency import AppDependency
from internal.auth.handler import createAuthRouter
from internal.gmail.handler import createGmailRouter
from internal.platform.config.Settings import Settings
from internal.platform.database.Dependency import createAsyncSessionMaker
from internal.platform.database.PostgresSQLSetup import closePostgresSQL, createAsyncEngine, initPostgresSQL


def buildAppDependencies():
    settings = Settings()
    asyncEngine = createAsyncEngine(settings=settings)
    asyncSessionMaker = createAsyncSessionMaker(asyncEngine=asyncEngine)
    applicationDependency = AppDependency(
        settings=settings, asyncEngine=asyncEngine, asyncSessionMaker=asyncSessionMaker
    )
    return applicationDependency


applicationDependency = buildAppDependencies()


@asynccontextmanager
async def appLifespan(app: FastAPI):
    await initPostgresSQL(asyncEngine=applicationDependency.asyncEngine)
    yield
    await closePostgresSQL(asyncEngine=applicationDependency.asyncEngine)


app = FastAPI(debug=True, version="0.1.0", title="Invoice Intelligence", lifespan=appLifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="secret")


app.include_router(createAuthRouter(applicationDependency=applicationDependency))
app.include_router(createGmailRouter(applicationDependency=applicationDependency))
