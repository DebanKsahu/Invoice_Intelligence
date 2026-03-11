from typing import List

from pydantic import BaseModel, Field


class ImageSummary(BaseModel):
    image_id: str
    caption: str = Field("", description="Caption text if present")
    summary: str = Field(..., description="Concise summary of the embedded image/figure")
    ocr_text: str = Field("", description="Text found inside the embedded image, if any")


class PdfPageSummary(BaseModel):
    page_summary: str = Field(
        ..., description="Concise, page-level summary suitable for RAG (1-3 paragraphs)"
    )
    images: List[ImageSummary] = Field(
        ..., description="List of summaries of embedded images/figures on the page"
    )

    def toText(self):
        textArr: List[str] = []

        textArr.append("[PAGE_SUMMARY]")
        textArr.append(self.page_summary.strip())
        textArr.append("")

        images = self.images or []
        textArr.append("[IMAGES]")
        textArr.append(f"COUNT: {len(images)}")
        textArr.append("")

        for img in images:
            textArr.append("[IMAGE]")
            textArr.append(f"ID: {img.image_id}")
            textArr.append(f"CAPTION: {img.caption.strip() if img.caption else ''}")
            textArr.append(f"OCR: {img.ocr_text.strip() if img.ocr_text else ''}")
            textArr.append(f"SUMMARY: {img.summary.strip()}")
            textArr.append("")  # separator between images

        return "\n".join(textArr).strip()