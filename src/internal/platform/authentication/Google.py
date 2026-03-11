from google_auth_oauthlib.flow import Flow

from internal.platform.authentication.Scopes import GOOGLE_AUTH_SCOPES, GOOGLE_GMAIL_SCOPES
from internal.platform.config.Settings import Settings


def createClientConfig(settings: Settings):
    return {
        "web": {
            "client_id": settings.googleSettings.CLIENT_ID,
            "client_secret": settings.googleSettings.CLIENT_SECRET,
            "auth_uri": settings.googleSettings.AUTH_URI,
            "token_uri": settings.googleSettings.TOKEN_URI,
        }
    }


def createAuthFlow(settings: Settings, originalState: str | None = None):
    if originalState is None:
        return Flow.from_client_config(
            client_config=createClientConfig(settings=settings),
            scopes=GOOGLE_GMAIL_SCOPES + GOOGLE_AUTH_SCOPES,
            redirect_uri=settings.googleSettings.AUTH_CALLBACK_URL,
        )
    else:
        return Flow.from_client_config(
            client_config=createClientConfig(settings=settings),
            scopes=GOOGLE_GMAIL_SCOPES + GOOGLE_AUTH_SCOPES,
            redirect_uri=settings.googleSettings.AUTH_CALLBACK_URL,
            state=originalState,
        )
