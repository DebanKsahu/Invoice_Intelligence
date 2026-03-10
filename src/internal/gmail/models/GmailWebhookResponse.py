from pydantic import BaseModel, Field


class GmailWebhookResponse(BaseModel):
    ok: bool
    reason: str | None = Field(default=None)
