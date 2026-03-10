import base64
from datetime import datetime, timezone
from typing import Dict

import msgspec
from google.auth.external_account_authorized_user import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials as OAuthCredentils
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.gmail import repository
from internal.gmail.models.GmailWebhookResponse import GmailWebhookResponse
from internal.platform.config.Settings import Settings


def createGmailObserver(userCredentails: Credentials | OAuthCredentils, settings: Settings):
    gmailService = build("gmail", "v1", credentials=userCredentails)

    requestBody = {
        "labelIds": ["INBOX"],
        "topicName": settings.googleSettings.GMAIL_PUBSUB_TOPIC_NAME,
    }

    response = gmailService.users().watch(userId="me", body=requestBody).execute()

    return response


async def handleGmailWebhook(requestBody: Dict, asyncSession: AsyncSession, settings: Settings) -> GmailWebhookResponse:
    message = requestBody.get("message", {})
    if "data" not in message:
        return GmailWebhookResponse(ok=False, reason="no data")
    rawPayload = base64.b64decode(message["data"])
    payload = msgspec.json.decode(rawPayload)

    userEmail = payload["emailAddress"]
    newGmailHistoryId = int(payload["historyId"])

    user = await repository.getUserByEmail(userEmail=userEmail, asyncSession=asyncSession)

    if user is None:
        return GmailWebhookResponse(ok=True)
    else:
        newUserCredentials = OAuthCredentils(
            token=None,
            refresh_token=user.refreshToken,
            token_uri=settings.googleSettings.TOKEN_URI,
            client_id=settings.googleSettings.CLIENT_ID,
            client_secret=settings.googleSettings.CLIENT_SECRET,
        )
        newUserCredentials.refresh(GoogleRequest())

        gmailService = build("gmail", "v1", credentials=newUserCredentials)

        try:
            if user.gmailHistoryId is not None:
                historyResponse = (
                    gmailService.users().history().list(userId="me", startHistoryId=user.gmailHistoryId)
                )
            else:
                historyResponse = (
                    gmailService.users().history().list(userId="me", startHistoryId=newGmailHistoryId)
                )

            messageIds = []
            for history in historyResponse.get("history", []):
                for message in history.get("messagesAdded", []):
                    messageId = message["message"]["id"]
                    messageIds.append(messageId)

            if len(messageIds) == 0:
                messageIds = fullGmailUnreadFallback(gmailService=gmailService)
            for messageId in messageIds:
                messageDetail = (
                    gmailService.users().messages().get(userId="me", id=messageId, format="full").execute()
                )
                # Handle The Message Like Extracting The Invoice Details Etc
            newGmailHistoryId = max(
                newGmailHistoryId, int(historyResponse.get("historyId", newGmailHistoryId))
            )
            user.gmailHistoryId = newGmailHistoryId
            asyncSession.add(user)
            await asyncSession.commit()

        except HttpError:
            messageIds = fullGmailSyncFallback(gmailService=gmailService)
            for messageId in messageIds:
                messageDetail = (
                    gmailService.users().messages().get(userId="me", id=messageId, format="full").execute()
                )
                # Handle The Message Like Extracting The Invoice Details Etc

            newGmailObserverResponse = createGmailObserver(
                userCredentails=newUserCredentials, settings=settings
            )
            user.gmailHistoryId = int(newGmailObserverResponse["historyId"])
            user.gmailObserverExpiry = datetime.fromtimestamp(
                timestamp=int(newGmailObserverResponse["expiration"]) / 1000, tz=timezone.utc
            )
            asyncSession.add(user)
            await asyncSession.commit()
        return GmailWebhookResponse(ok=True)


def fullGmailUnreadFallback(gmailService):
    gmailServiceResponse = (
        gmailService.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=50)
        .execute()
    )
    return [message["id"] for message in gmailServiceResponse.get("messages", [])]


def fullGmailSyncFallback(gmailService):
    gmailServiceResponse = (
        gmailService.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=200).execute()
    )
    return [message["id"] for message in gmailServiceResponse.get("messages", [])]
