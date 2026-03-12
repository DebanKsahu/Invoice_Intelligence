from dataclasses import dataclass


@dataclass(frozen=True)
class GmailAttachmentDetail:
    filename: str
    filebytes: bytes | bytearray
