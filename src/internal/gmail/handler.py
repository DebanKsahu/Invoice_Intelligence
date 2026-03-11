from fastapi import APIRouter, Request

from core.AppDependency import AppDependency
from internal.gmail import service
from internal.gmail.models.GmailWebhookResponse import GmailWebhookResponse


def createGmailRouter(applicationDependency: AppDependency) -> APIRouter:
    gmailRouter = APIRouter(prefix="/gmail", tags=["Gmail"])

    @gmailRouter.post("/webhook")
    async def gmailWebhook(request: Request) -> GmailWebhookResponse:
        requestBody = await request.json()
        async with applicationDependency.getAsyncSession() as asyncSession:
            response = await service.handleGmailWebhook(
                requestBody=requestBody,
                asyncSession=asyncSession,
                settings=applicationDependency.settings,
                logger=applicationDependency.logger,
            )
        return response

    return gmailRouter
