from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from core.AppDependency import AppDependency
from internal.auth import service
from internal.auth.models.AuthCredentials import AuthCredentials


def createAuthRouter(applicationDependency: AppDependency) -> APIRouter:
    authRouter = APIRouter(prefix="/auth")

    @authRouter.get("/gmail/initAuth")
    async def startAuth(request: Request) -> RedirectResponse:
        authUrl, state = service.handleStartAuth(settings=applicationDependency.settings)
        request.session["oauthState"] = state
        return RedirectResponse(authUrl)

    @authRouter.get("/gmail/callback")
    async def authCallback(request: Request) -> AuthCredentials:
        receivedState = request.query_params.get("state", "receivedState")
        originalState = request.session.get("oauthState", "OriginalState")
        receivedCode = request.query_params.get("code", "receivedCode")

        async with applicationDependency.getAsyncSession() as session:
            userCredentials = await service.handleAuthCallback(
                settings=applicationDependency.settings,
                receivedState=receivedState,
                originalState=originalState,
                receivedCode=receivedCode,
                asyncSession=session,
            )

        return userCredentials

    return authRouter
