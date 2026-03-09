from pydantic import BaseModel


class GoogleSettings(BaseModel):
    CLIENT_ID: str
    CLIENT_SECRET: str
    AUTH_URI: str
    TOKEN_URI: str

    AUTH_CALLBACK_URL: str

    GMAIL_PUBSUB_TOPIC_NAME: str
    GMAIL_PUBSUB_CALLBACK_URL: str
