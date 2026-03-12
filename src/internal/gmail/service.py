import base64
from datetime import datetime, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import Logger
from typing import Dict, List

import msgspec
from google.auth.external_account_authorized_user import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials as OAuthCredentils
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.gmail import repository
from internal.gmail.models.GmailAttachment import GmailAttachment
from internal.gmail.models.GmailAttachmentDetail import GmailAttachmentDetail
from internal.gmail.models.GmailMessage import GmailMessage
from internal.gmail.models.GmailWebhookResponse import GmailWebhookResponse
from internal.gmail.models.UserEmailDetail import UserEmailDetail
from internal.platform.config.Settings import Settings

ALLOWED_INVOICE_MIME = {"application/pdf", "image/png", "image/jpeg", "image/jpg", "image/tiff", "image/webp"}

ALLOWED_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".webp")


def createGmailObserver(userCredentails: Credentials | OAuthCredentils, settings: Settings):
    gmailService = build("gmail", "v1", credentials=userCredentails)

    requestBody = {
        "labelIds": ["INBOX"],
        "topicName": settings.googleSettings.GMAIL_PUBSUB_TOPIC_NAME,
    }

    response = gmailService.users().watch(userId="me", body=requestBody).execute()

    return response


async def handleGmailWebhook(
    requestBody: Dict, asyncSession: AsyncSession, settings: Settings, logger: Logger
) -> GmailWebhookResponse:
    message = requestBody.get("message", {})
    logger.info(f"Got the message from google {message}")
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
                    gmailService.users()
                    .history()
                    .list(userId="me", startHistoryId=user.gmailHistoryId)
                    .execute()
                )
            else:
                historyResponse = (
                    gmailService.users()
                    .history()
                    .list(userId="me", startHistoryId=newGmailHistoryId)
                    .execute()
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

                invoiceFiles = extractInvoiceFiles(gmailService=gmailService, messageDetail=messageDetail)
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


def collectAttachments(payloadParts, attachmentsList: List[GmailAttachment]):
    for part in payloadParts:
        fileName = part.get("filename")
        mimeType = part.get("mimeType")
        body = part.get("body", {})

        if fileName and "attachmentId" in body:
            attachmentsList.append(
                GmailAttachment(fileName=fileName, mimeType=mimeType, attachmentId=body["attachmentId"])
            )

        if "parts" in body:
            collectAttachments(part["parts"], attachmentsList)


def extractAttachmentFromMessage(messageDetail) -> List[GmailAttachment]:
    attachments: list[GmailAttachment] = []

    payload = messageDetail.get("payload", {})

    if "parts" in payload:
        collectAttachments(payload["parts"], attachments)

    return attachments


def filterInvoiceAttachments(attachmentsList: List[GmailAttachment]) -> List[GmailAttachment]:
    finalAttachments = []
    for attachment in attachmentsList:
        if attachment.mimeType in ALLOWED_INVOICE_MIME:
            finalAttachments.append(attachment)

        elif attachment.fileName.lower().endswith(ALLOWED_EXTENSIONS):
            finalAttachments.append(attachment)

    return finalAttachments


def downloadAttachment(gmailService, messageId, attachment: GmailAttachment) -> bytes:
    response = (
        gmailService.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=messageId, id=attachment.attachmentId)
        .execute()
    )

    return base64.urlsafe_b64decode(response["data"])


def extractInvoiceFiles(gmailService, messageDetail):
    messageId = messageDetail["id"]

    attachments = extractAttachmentFromMessage(messageDetail)

    invoiceFiles = filterInvoiceAttachments(attachments)

    files = []

    for attachment in invoiceFiles:
        file_bytes = downloadAttachment(gmailService, messageId, attachment)

        files.append(
            {
                "filename": attachment.fileName,
                "mime_type": attachment.mimeType,
                "data": file_bytes,
            }
        )

    return files


def createGmailMessage(
    userDetail: UserEmailDetail, subject: str, body: str, attachmentDetail: GmailAttachmentDetail | None
):
    if attachmentDetail is None:
        message = MIMEText(body)
        message["to"] = userDetail.email
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        return GmailMessage(raw=raw)
    else:
        message = MIMEMultipart()

        message["to"] = userDetail.email
        message["subject"] = subject

        message.attach(MIMEText(body))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachmentDetail.filebytes)

        encoders.encode_base64(part)

        part.add_header("Content-Disposition", f'attachment; filename="{attachmentDetail.filename}"')

        message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return GmailMessage(raw=raw)


def sendEmail(
    gmailService,
    userDetail: UserEmailDetail,
    subject: str,
    body: str,
    attachmentDetail: GmailAttachmentDetail | None,
):
    message = createGmailMessage(
        userDetail=userDetail, subject=subject, body=body, attachmentDetail=attachmentDetail
    )
    gmailService.users().messages().send(userId="me", body=message.toDict()).execute()
