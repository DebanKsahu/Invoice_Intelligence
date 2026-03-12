from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GmailMessage:
    raw: str

    def toDict(self):
        return {"raw": self.raw}
