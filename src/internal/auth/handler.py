import logging

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from core.AppDependency import AppDependency
from internal.auth import service
from internal.auth.models.AuthCredentials import AuthCredentials


def createAuthRouter(applicationDependency: AppDependency) -> APIRouter:
    authRouter = APIRouter(prefix="/auth", tags=["Authentication"])

    @authRouter.get("/gmail/initAuth")
    async def startAuth(request: Request) -> RedirectResponse:
        logger = logging.getLogger(__name__)
        logger.info("Starting Gmail OAuth authentication flow")
        authUrl, state, codeVerifier = service.handleStartAuth(settings=applicationDependency.settings)
        request.session["oauthState"] = state
        request.session["codeVerifier"] = codeVerifier
        logger.debug(f"OAuth state generated: {state[:20]}...")
        return RedirectResponse(authUrl)

    @authRouter.get("/gmail/callback")
    async def authCallback(request: Request) -> AuthCredentials:
        logger = logging.getLogger(__name__)
        receivedState = request.query_params.get("state", "receivedState")
        originalState = request.session.pop("oauthState", "OriginalState")
        receivedCode = request.query_params.get("code", "receivedCode")
        originalCodeVerifier = request.session.pop("codeVerifier", None)

        logger.info("Processing OAuth callback")

        async with applicationDependency.getAsyncSession() as session:
            userAuthCredentials = await service.handleAuthCallback(
                settings=applicationDependency.settings,
                receivedState=receivedState,
                originalState=originalState,
                receivedCode=receivedCode,
                originalCodeVerifier=originalCodeVerifier,
                asyncSession=session,
            )

        logger.info("OAuth callback successfull processed")
        return userAuthCredentials

    return authRouter
