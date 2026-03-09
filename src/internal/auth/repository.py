from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from internal.auth.models.AuthCredentials import AuthCredentials
from internal.auth.models.GoogleUserInfo import GoogleUserInfo
from internal.platform.database.models.UserInDatabase import UserInDatabase


async def createNewUser(
    userInfo: GoogleUserInfo,
    userCredentials: AuthCredentials,
    asyncSession: AsyncSession,
):
    newUser = UserInDatabase(
        name=userInfo.name,
        email=userInfo.email,
        googleSub=userInfo.googleSub,
        refreshToken=userCredentials.refreshToken,
        currAccessToken=userCredentials.accessToken,
        currAccessTokenExpiry=userCredentials.accessTokenExpiry,
    )

    asyncSession.add(newUser)
    await asyncSession.commit()


async def updateUser(userInfo: GoogleUserInfo, userCredentials: AuthCredentials, asyncSession: AsyncSession):
    existingUser = await getUserByGoogleSub(userGoogleSub=userInfo.googleSub, asyncSession=asyncSession)
    if existingUser is None:
        raise
    else:
        existingUser.name = userInfo.name
        existingUser.email = userInfo.email
        existingUser.googleSub = userInfo.googleSub
        existingUser.refreshToken = userCredentials.refreshToken
        existingUser.currAccessToken = userCredentials.accessToken
        existingUser.currAccessTokenExpiry = userCredentials.accessTokenExpiry

        asyncSession.add(existingUser)
        await asyncSession.commit()


async def getUserByGoogleSub(userGoogleSub: str, asyncSession: AsyncSession):
    sqlStatement = select(UserInDatabase).where(UserInDatabase.googleSub == userGoogleSub)
    userDetail = (await asyncSession.execute(sqlStatement)).scalar_one_or_none()

    if userDetail is None:
        raise
    else:
        return userDetail
