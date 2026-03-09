from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.AppDependency import AppDependency
from internal.auth.handler import createAuthRouter


@asynccontextmanager
async def appLifespan(app: FastAPI):
    yield


app = FastAPI(debug=True, version="0.1.0", title="", lifespan=appLifespan)
applicationDependencies: AppDependency = app.state.di
app.include_router(createAuthRouter(applicationDependency=applicationDependencies))

if __name__ == "__main__":
    pass
