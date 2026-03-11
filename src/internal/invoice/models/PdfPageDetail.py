from dataclasses import dataclass


@dataclass(frozen=True)
class PdfPageDetail:
    pageNum: int
    numImage: int
    pageContext: str
