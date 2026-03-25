import base64
from typing import List

from internal.gmail.constant import ALLOWED_INVOICE_EXTENSIONS, ALLOWED_INVOICE_MIME
from internal.gmail.models.GmailAttachment import GmailAttachment


def extractInvoiceFiles(gmailService, messageDetail):
    messageId = messageDetail["id"]

    attachments = extractAttachmentFromMessage(messageDetail)

    invoiceFiles = filterInvoiceAttachments(attachments)

    files = []

    for attachment in invoiceFiles:
        file_bytes = downloadAttachment(gmailService, messageId, attachment)

        files.append(
            {
                "fileName": attachment.fileName,
                "mime_type": attachment.mimeType,
                "data": file_bytes,
            }
        )

    return files


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
    headers = payload.get("headers", [])

    for header in headers:
        if header.get("name", "").lower() == "subject":
            if header.get("value", "") == "Invoice Intelligence: Reply":
                return attachments

    if "parts" in payload:
        collectAttachments(payload["parts"], attachments)

    return attachments


def filterInvoiceAttachments(attachmentsList: List[GmailAttachment]) -> List[GmailAttachment]:
    finalAttachments = []
    for attachment in attachmentsList:
        if attachment.mimeType in ALLOWED_INVOICE_MIME:
            finalAttachments.append(attachment)

        elif attachment.fileName.lower().endswith(ALLOWED_INVOICE_EXTENSIONS):
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
