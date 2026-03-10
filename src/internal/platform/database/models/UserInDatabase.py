from datetime import datetime
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class UserInDatabase(SQLModel, table=True):
    userId: UUID = Field(primary_key=True, default_factory=uuid7)
    name: str = Field(min_length=1)
    email: str = Field(min_length=1, index=True, unique=True)

    googleSub: str = Field(min_length=1, index=True, unique=True)

    refreshToken: str = Field(min_length=1)
    currAccessToken: str = Field(min_length=1)
    currAccessTokenExpiry: datetime

    gmailObserverExpiry: datetime
    gmailHistoryId: int | None = Field(default=None)
