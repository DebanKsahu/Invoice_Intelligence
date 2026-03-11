import httpx
import msgspec
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from internal.auth import repository
from internal.auth.models.AuthCredentials import AuthCredentials
from internal.auth.models.GoogleUserInfo import GoogleUserInfo
from internal.platform.authentication.Google import createAuthFlow
from internal.platform.config.Settings import Settings


def handleStartAuth(settings: Settings):
    flow = createAuthFlow(settings=settings)
    authUrl, state = flow.authorization_url(access_type="offline", prompt="consent")
    return authUrl, state, flow.code_verifier


async def handleAuthCallback(
    settings: Settings,
    receivedState: str,
    originalState: str,
    receivedCode: str,
    originalCodeVerifier: str | None,
    asyncSession: AsyncSession,
):
    if receivedState != originalState:
        raise HTTPException(status_code=500)
    flow = createAuthFlow(settings=settings, originalState=originalState)
    flow.code_verifier = originalCodeVerifier
    try:
        flow.fetch_token(code=receivedCode)
        credentials = flow.credentials

        userCredentails = AuthCredentials.createFromCredentials(userCredentials=credentials)

        async with httpx.AsyncClient() as asyncClient:
            response = await asyncClient.get(
                url="https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
            response.raise_for_status()
            jsonResponse = msgspec.json.decode(response.content)
            userInfo = GoogleUserInfo(
                googleSub=jsonResponse["sub"], name=jsonResponse["name"], email=jsonResponse["email"]
            )

        existingUser = await repository.getUserByGoogleSub(
            userGoogleSub=userInfo.googleSub, asyncSession=asyncSession
        )

        if existingUser is None:
            await repository.createNewUser(
                userInfo=userInfo,
                userCredentials=userCredentails,
                asyncSession=asyncSession,
            )
        else:
            await repository.updateUser(
                userInfo=userInfo,
                userCredentials=userCredentails,
                asyncSession=asyncSession,
            )

        return userCredentails
    except:
        raise
