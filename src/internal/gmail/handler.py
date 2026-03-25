from fastapi import APIRouter, BackgroundTasks, Request

from core.AppDependency import AppDependency
from internal.gmail.models.GmailWebhookResponse import GmailWebhookResponse
from internal.gmail.services import core_service


def createGmailRouter(applicationDependency: AppDependency) -> APIRouter:
    gmailRouter = APIRouter(prefix="/gmail", tags=["Gmail"])

    @gmailRouter.post("/webhook")
    async def gmailWebhook(request: Request, backgroundTasks: BackgroundTasks) -> GmailWebhookResponse:
        requestBody = await request.json()
        async with applicationDependency.getAsyncSession() as asyncSession:
            response = await core_service.handleGmailWebhook(
                requestBody=requestBody,
                asyncSession=asyncSession,
                settings=applicationDependency.settings,
            )
        return response

    return gmailRouter
