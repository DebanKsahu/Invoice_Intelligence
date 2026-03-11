from pydantic import BaseModel


class LlmWhispererSettings(BaseModel):
    API_KEY: str
    BASE_URL: str
