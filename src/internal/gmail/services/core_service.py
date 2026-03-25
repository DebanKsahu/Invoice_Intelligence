import base64
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Dict

import msgspec
from fastapi import BackgroundTasks
from google.auth.external_account_authorized_user import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials as OAuthCredentils
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.gmail import repository
from internal.gmail.models.GmailAttachmentDetail import GmailAttachmentDetail
from internal.gmail.models.GmailWebhookResponse import GmailWebhookResponse
from internal.gmail.models.UserEmailDetail import UserEmailDetail
from internal.gmail.services.data_extraction_service import extractInvoiceFiles
from internal.gmail.services.mail_service import sendEmail
from internal.invoice.service import constructPdfDetail, extractDetailFromInvoice, validateInvoice
from internal.invoice.services.InvoiceDataFormatService import createInvoiceExcelSheet
from internal.platform.config.Settings import Settings


def createGmailObserver(userCredentails: Credentials | OAuthCredentils, settings: Settings):
    gmailService = build("gmail", "v1", credentials=userCredentails)

    requestBody = {
        "labelIds": ["INBOX"],
        "topicName": settings.googleSettings.GMAIL_PUBSUB_TOPIC_NAME,
    }

    response = gmailService.users().watch(userId="me", body=requestBody).execute()

    return response


async def handleGmailWebhook(
    requestBody: Dict, asyncSession: AsyncSession, settings: Settings, backgroundTasks: BackgroundTasks
) -> GmailWebhookResponse:
    logger = logging.getLogger(__name__)
    message = requestBody.get("message", {})
    logger.info("Processing Gmail webhook message")

    if "data" not in message:
        logger.warning("Webhook message missing 'data' field")
        return GmailWebhookResponse(ok=False, reason="no data")

    rawPayload = base64.b64decode(message["data"])
    payload = msgspec.json.decode(rawPayload)

    userEmail = payload["emailAddress"]
    newGmailHistoryId = int(payload["historyId"])
    logger.info(f"Processing webhook for user: {userEmail}, historyId: {newGmailHistoryId}")

    user = await repository.getUserByEmail(userEmail=userEmail, asyncSession=asyncSession)

    if user is None:
        logger.warning(f"Webhook received for unknown user: {userEmail}")
        return GmailWebhookResponse(ok=True)
    if user.gmailHistoryId is not None and newGmailHistoryId <= user.gmailHistoryId:
        logger.info(f"Skipping old Pub/Sub event. incoming={newGmailHistoryId}, stored={user.gmailHistoryId}")
        return GmailWebhookResponse(ok=True)

    logger.debug(f"Found user in database: {user.email}")

    newUserCredentials = OAuthCredentils(
        token=None,
        refresh_token=user.refreshToken,
        token_uri=settings.googleSettings.TOKEN_URI,
        client_id=settings.googleSettings.CLIENT_ID,
        client_secret=settings.googleSettings.CLIENT_SECRET,
    )
    newUserCredentials.refresh(GoogleRequest())
    logger.debug("User credentials refreshed successfully")

    gmailService = build("gmail", "v1", credentials=newUserCredentials)

    newGmailObserverResponse = createGmailObserver(userCredentails=newUserCredentials, settings=settings)
    user.gmailHistoryId = newGmailHistoryId
    user.gmailObserverExpiry = datetime.fromtimestamp(
        timestamp=int(newGmailObserverResponse["expiration"]) / 1000, tz=timezone.utc
    )

    userEmailDetail = UserEmailDetail(name=user.name, email=user.email)

    asyncSession.add(user)
    await asyncSession.commit()

    backgroundTasks.add_task(
        processMessages,
        gmailService=gmailService,
        gmailHistoryId=newGmailHistoryId,
        userEmailDetail=userEmailDetail,
        settings=settings,
    )

    return GmailWebhookResponse(ok=True)


def getUnprocessedMessages(gmailService, gmailHistoryId: int):
    logger = logging.getLogger(__name__)
    historyResponse = (
        gmailService.users().history().list(userId="me", startHistoryId=gmailHistoryId).execute()
    )

    messageIds = []
    for history in historyResponse.get("history", []):
        for message in history.get("messagesAdded", []):
            messageId = message["message"]["id"]
            messageIds.append(messageId)

    logger.info(f"Found {len(messageIds)} new messages in history")
    return messageIds


async def processMessages(
    gmailService, gmailHistoryId: int, userEmailDetail: UserEmailDetail, settings: Settings
):
    logger = logging.getLogger(__name__)
    try:
        logger.debug(f"Fetching Gmail history from historyId: {gmailHistoryId}")
        messageIds = getUnprocessedMessages(gmailService=gmailService, gmailHistoryId=gmailHistoryId)
        for messageId in messageIds:
            try:
                messageDetail = (
                    gmailService.users().messages().get(userId="me", id=messageId, format="full").execute()
                )
                invoiceFiles = extractInvoiceFiles(gmailService=gmailService, messageDetail=messageDetail)
                logger.debug(f"Found {len(invoiceFiles)} invoice files in message {messageId}")

                invoiceDetailList = []

                for invoiceFile in invoiceFiles:
                    fileName = invoiceFile.get("fileName", None)
                    fileBytes = invoiceFile.get("data", None)
                    if isinstance(fileName, str) and isinstance(fileBytes, bytes):
                        fileStream = BytesIO(fileBytes)
                        logger.debug(f"Processing invoice file: {fileName} ({len(fileBytes)} bytes)")

                        pdfDetail = await constructPdfDetail(
                            fileName=fileName, fileStream=fileStream, settings=settings
                        )
                        isInvoiceDetail = await validateInvoice(pdfDetail=pdfDetail, settings=settings)
                        if isInvoiceDetail.isInvoice:
                            logger.info(f"Valid invoice detected: {fileName}")
                            invoiceDetail = await extractDetailFromInvoice(
                                pdfDetail=pdfDetail, settings=settings
                            )
                            invoiceDetailList.append(invoiceDetail)
                        else:
                            logger.debug(f"File {fileName} is not a valid invoice")

                if len(invoiceDetailList) > 0:
                    sendEmail(
                        gmailService=gmailService,
                        userEmailDetail=userEmailDetail,
                        subject="Invoice Intelligence: Reply",
                        body="Your Invoice Excel Sheet",
                        attachmentDetail=GmailAttachmentDetail(
                            filename="Invoices.xlsx",
                            filebytes=createInvoiceExcelSheet(invoiceDetails=invoiceDetailList),
                        ),
                    )
                    logger.info(f"Invoice details sent to user: {userEmailDetail.email}")

            except Exception as e:
                logger.error(f"Error processing message {messageId}: {str(e)}", exc_info=True)
    except HttpError as e:
        logger.warning(f"Gmail API error, falling back to sync method: {str(e)}", exc_info=True)
        messageIds = fullGmailSyncFallback(gmailService=gmailService)
        logger.info(f"Fallback sync found {len(messageIds)} messages")

        for messageId in messageIds:
            messageDetail = (
                gmailService.users().messages().get(userId="me", id=messageId, format="full").execute()
            )

            invoiceFiles = extractInvoiceFiles(gmailService=gmailService, messageDetail=messageDetail)
            invoiceDetailList = []

            for invoiceFile in invoiceFiles:
                fileName = invoiceFile.get("fileName", None)
                fileBytes = invoiceFile.get("data", None)
                if isinstance(fileName, str) and isinstance(fileBytes, bytes):
                    fileStream = BytesIO(fileBytes)
                    logger.debug(f"Processing invoice file (fallback): {fileName}")

                    pdfDetail = await constructPdfDetail(
                        fileName=fileName, fileStream=fileStream, settings=settings
                    )
                    isInvoiceDetail = await validateInvoice(pdfDetail=pdfDetail, settings=settings)
                    if isInvoiceDetail.isInvoice:
                        logger.info(f"Valid invoice detected (fallback): {fileName}")
                        invoiceDetail = await extractDetailFromInvoice(pdfDetail=pdfDetail, settings=settings)
                        invoiceDetailList.append(invoiceDetail)
            if len(invoiceDetailList) > 0:
                sendEmail(
                    gmailService=gmailService,
                    userEmailDetail=userEmailDetail,
                    subject="Invoice Intelligence: Reply",
                    body="Your Invoice Excel Sheet",
                    attachmentDetail=GmailAttachmentDetail(
                        filename="Invoices.xlsx",
                        filebytes=createInvoiceExcelSheet(invoiceDetails=invoiceDetailList),
                    ),
                )
                logger.info(f"Invoice details sent to user (fallback): {userEmailDetail.email}")


def fullGmailSyncFallback(gmailService):
    gmailServiceResponse = (
        gmailService.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=200).execute()
    )
    return [message["id"] for message in gmailServiceResponse.get("messages", [])]
