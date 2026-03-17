import asyncio
import base64
from pathlib import Path
from typing import IO, Dict, List

import aiofiles
import fitz
from fastapi import HTTPException
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from pymupdf import Document
from unstract.llmwhisperer import LLMWhispererClientV2

from core.Enums import DirectoryPaths
from internal.invoice.models.InvoiceDetail import InvoiceDetail
from internal.invoice.models.InvoiceValidation import InvoiceValidation
from internal.invoice.models.PdfDetail import PdfDetail
from internal.invoice.models.PdfPageDetail import PdfPageDetail
from internal.invoice.models.PdfPageSummary import PdfPageSummary
from internal.platform.config.Settings import Settings
from internal.platform.prompts.ImageSummarizePrompt import (
    imageSummarizeDetailOutputInstruction,
    imageSummarizeTaskInstruction,
)
from internal.platform.prompts.InvoiceDataExtractionPrompt import (
    invoiceDataExtractionDetailOutputInstruction,
    invoiceDataExtractionTaskInstruction,
)
from internal.platform.prompts.InvoiceValidationPrompt import (
    invoiceValidationOutputInstruction,
    invoiceValidationTaskInstruction,
)


def createLlmWhispererClient(settings: Settings) -> LLMWhispererClientV2:
    llmWhispererClient = LLMWhispererClientV2(
        base_url=settings.llmWhispererSettings.BASE_URL, api_key=settings.llmWhispererSettings.API_KEY
    )
    return llmWhispererClient


async def extractTextFromPdf(fileStream: IO[bytes], settings: Settings) -> List[str]:
    llmWhispererClient = createLlmWhispererClient(settings=settings)
    response = llmWhispererClient.whisper(stream=fileStream, mode="native_text", page_seperator="<<-->>")
    responseWhisperHash: str = response.get("whisper_hash")

    result: Dict | None = None

    while True:
        retrivalStatus = llmWhispererClient.whisper_status(whisper_hash=responseWhisperHash)
        if retrivalStatus.get("status") == "processed":
            result = llmWhispererClient.whisper_retrieve(whisper_hash=responseWhisperHash)
            break
        await asyncio.sleep(3.0)

    extractedText: str = result.get("extraction").get("result_text")
    extractedTextArr = extractedText.split("<<-->>")

    return extractedTextArr


async def constructPdfDetail(fileName: str, fileStream: IO[bytes], settings: Settings) -> PdfDetail:
    docName = fileName
    doc = fitz.open(stream=fileStream)
    allPageDetails = []

    extractedTextArr = await extractTextFromPdf(fileStream=fileStream, settings=settings)

    currPageNum = 1
    for page in doc:
        images = page.get_images(full=True)
        numImage = len(images)

        if numImage == 0:
            pageDetail = PdfPageDetail(
                pageNum=currPageNum,
                numImage=numImage,
                pageContext=extractedTextArr[currPageNum - 1],
            )
            allPageDetails.append(pageDetail)
        else:
            imagePath = convertPageToImage(doc=doc, pageNumber=currPageNum - 1, docName=docName)
            imageSummary = await generateSummary(imagePath=imagePath, settings=settings)
            pageDetail = PdfPageDetail(
                pageNum=currPageNum,
                numImage=numImage,
                pageContext=imageSummary.toText(),
            )

        currPageNum += 1

    pdfDetail = PdfDetail(numPage=currPageNum - 1, pageDetails=allPageDetails, pdfName=docName)

    return pdfDetail


def convertPageToImage(doc: Document, pageNumber: int, docName: str):
    page = doc[pageNumber]

    pageImage = page.get_pixmap(dpi=300, alpha=False)
    finalImagePath = DirectoryPaths.UPLOAD_DIR.value / docName / f"page_{pageNumber}.png"
    finalImagePathParent = DirectoryPaths.UPLOAD_DIR.value / docName
    finalImagePathParent.mkdir(parents=True, exist_ok=True)
    pageImage.save(finalImagePath)

    return finalImagePath


async def encodeImage(imagePath: Path) -> str:
    async with aiofiles.open(imagePath, "rb") as imageFile:
        image = await imageFile.read()
    return base64.b64encode(image).decode()


def buildHumanMessageTextPart(inputText: str) -> Dict[str, str]:
    return {"type": "text", "text": inputText}


def buildHumanMessageImagePart(encodedImage: str) -> Dict[str, str]:
    return {"type": "image_url", "image_url": f"data:image/png;base64,{encodedImage}"}


def constructHumanMessage(*messageParts) -> HumanMessage:
    message = HumanMessage(content=list(messageParts))
    return message


def createGoogleGeminiLLM(settings: Settings) -> ChatGoogleGenerativeAI:
    googleGeminiLLM = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview", api_key=settings.googleGeminiSettings.API_KEY
    )
    return googleGeminiLLM


def createStructuredLLM(llm: ChatGoogleGenerativeAI, schema: type[BaseModel]):
    return llm.with_structured_output(schema=schema)


async def generateSummary(imagePath: Path, settings: Settings) -> PdfPageSummary:
    googleGeminiLLM = createGoogleGeminiLLM(settings=settings)
    googleGeminiStructuredLLM = createStructuredLLM(llm=googleGeminiLLM, schema=PdfPageSummary)

    encodedImageData = await encodeImage(imagePath=imagePath)

    message = constructHumanMessage(
        buildHumanMessageTextPart(inputText=imageSummarizeTaskInstruction),
        buildHumanMessageImagePart(encodedImage=encodedImageData),
        buildHumanMessageTextPart(inputText=imageSummarizeDetailOutputInstruction),
    )

    llmResponse = await googleGeminiStructuredLLM.ainvoke([message])
    try:
        finalResponse = PdfPageSummary.model_validate(llmResponse, extra="ignore")
        return finalResponse
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to validate PDF page summary response")


async def validateInvoice(pdfDetail: PdfDetail, settings: Settings) -> InvoiceValidation:
    fullPdfText = ("\n\n").join([pageDetail.pageContext for pageDetail in pdfDetail.pageDetails])

    googleGeminiLLM = createGoogleGeminiLLM(settings=settings)
    googleGeminiStructuredLLM = createStructuredLLM(llm=googleGeminiLLM, schema=InvoiceValidation)

    message = constructHumanMessage(
        buildHumanMessageTextPart(inputText=invoiceValidationTaskInstruction),
        buildHumanMessageTextPart(inputText=f"[INVOICE TEXT HERE] \n\n {fullPdfText}"),
        buildHumanMessageTextPart(inputText=invoiceValidationOutputInstruction),
    )

    llmResponse = await googleGeminiStructuredLLM.ainvoke([message])
    try:
        finalResponse = InvoiceValidation.model_validate(llmResponse, extra="ignore")
        return finalResponse
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to validate invoice")


async def extractDetailFromInvoice(pdfDetail: PdfDetail, settings: Settings):
    fullPdfText = ("\n\n").join([pageDetail.pageContext for pageDetail in pdfDetail.pageDetails])

    googleGeminiLLM = createGoogleGeminiLLM(settings=settings)
    googleGeminiStructuredLLM = createStructuredLLM(llm=googleGeminiLLM, schema=InvoiceDetail)

    message = constructHumanMessage(
        buildHumanMessageTextPart(inputText=invoiceDataExtractionTaskInstruction),
        buildHumanMessageTextPart(inputText=f"[INVOICE TEXT HERE] \n\n {fullPdfText}"),
        buildHumanMessageTextPart(inputText=invoiceDataExtractionDetailOutputInstruction),
    )

    llmResponse = await googleGeminiStructuredLLM.ainvoke([message])
    try:
        finalResponse = InvoiceDetail.model_validate(llmResponse, extra="ignore")
        return finalResponse
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to extract fields from invoice")
