from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    DATABASE_URL: str
