from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from internal.platform.database.models.UserInDatabase import UserInDatabase


async def getUserByEmail(userEmail: str, asyncSession: AsyncSession):
    sqlStatement = select(UserInDatabase).where(UserInDatabase.email == userEmail)

    existingUser = (await asyncSession.execute(sqlStatement)).scalar_one_or_none()
    return existingUser
