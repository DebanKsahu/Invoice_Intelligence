from dataclasses import dataclass


@dataclass
class GmailAttachment:
    fileName: str
    mimeType: str
    attachmentId: str
