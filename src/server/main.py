import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.AppDependency import AppDependency
from core.LoggingConfig import setupLogging
from internal.auth.handler import createAuthRouter
from internal.gmail.handler import createGmailRouter
from internal.platform.config.Settings import Settings
from internal.platform.database.Dependency import createAsyncSessionMaker
from internal.platform.database.PostgresSQLSetup import closePostgresSQL, createAsyncEngine, initPostgresSQL


def buildAppDependencies():
    logger = setupLogging()

    logger.info("Initializing Invoice Intelligence application...")
    settings = Settings()
    asyncEngine = createAsyncEngine(settings=settings)
    asyncSessionMaker = createAsyncSessionMaker(asyncEngine=asyncEngine)
    applicationDependency = AppDependency(
        settings=settings, asyncEngine=asyncEngine, asyncSessionMaker=asyncSessionMaker
    )
    logger.debug("Application dependencies initialized successfully")
    return applicationDependency


applicationDependency = buildAppDependencies()


@asynccontextmanager
async def appLifespan(app: FastAPI):
    logger = logging.getLogger("invoice_intelligence")
    logger.info("🚀 Application startup: Initializing database...")
    await initPostgresSQL(asyncEngine=applicationDependency.asyncEngine)
    logger.info("✅ Database initialization completed")
    yield
    logger.info("🛑 Application shutdown: Closing database connection...")
    await closePostgresSQL(asyncEngine=applicationDependency.asyncEngine)
    logger.info("✅ Application shutdown completed")


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
