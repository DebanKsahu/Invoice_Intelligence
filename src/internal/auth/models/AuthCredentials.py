from dataclasses import dataclass
from datetime import datetime

from google.auth.external_account_authorized_user import Credentials
from google.oauth2.credentials import Credentials as OAuthCredentils


@dataclass(frozen=True, slots=True)
class AuthCredentials:
    accessToken: str
    refreshToken: str
    accessTokenExpiry: datetime

    @classmethod
    def createFromCredentials(cls, userCredentials: Credentials | OAuthCredentils):
        if not userCredentials.token:
            raise ValueError("Missing access token")

        if not userCredentials.refresh_token:
            raise ValueError("Missing refresh token")

        if not userCredentials.expiry:
            raise ValueError("Missing token expiry")

        return cls(
            accessToken=userCredentials.token,
            refreshToken=userCredentials.refresh_token,
            accessTokenExpiry=userCredentials.expiry,
        )
