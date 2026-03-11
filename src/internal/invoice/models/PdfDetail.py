from dataclasses import dataclass
from typing import List

from internal.invoice.models.PdfPageDetail import PdfPageDetail


@dataclass
class PdfDetail:
    numPage: int
    pageDetails: List[PdfPageDetail]
    pdfName: str

    def getPageTextArr(self):
        res = [pageDetail.pageContext for pageDetail in self.pageDetails]
        return res
