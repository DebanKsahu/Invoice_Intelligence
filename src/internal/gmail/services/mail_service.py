import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from internal.gmail.models.GmailAttachmentDetail import GmailAttachmentDetail
from internal.gmail.models.GmailMessage import GmailMessage
from internal.gmail.models.UserEmailDetail import UserEmailDetail


def createGmailMessage(
    userEmailDetail: UserEmailDetail, subject: str, body: str, attachmentDetail: GmailAttachmentDetail | None
):
    if attachmentDetail is None:
        message = MIMEText(body)
        message["to"] = userEmailDetail.email
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        return GmailMessage(raw=raw)
    else:
        message = MIMEMultipart()

        message["to"] = userEmailDetail.email
        message["subject"] = subject

        message.attach(MIMEText(body))

        part = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        part.set_payload(attachmentDetail.filebytes)

        encoders.encode_base64(part)

        part.add_header("Content-Disposition", f'attachment; filename="{attachmentDetail.filename}"')

        message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return GmailMessage(raw=raw)


def sendEmail(
    gmailService,
    userEmailDetail: UserEmailDetail,
    subject: str,
    body: str,
    attachmentDetail: GmailAttachmentDetail | None = None,
):
    message = createGmailMessage(
        userEmailDetail=userEmailDetail, subject=subject, body=body, attachmentDetail=attachmentDetail
    )
    gmailService.users().messages().send(userId="me", body=message.toDict()).execute()
