import io
from typing import List

import polars

from internal.invoice.models.InvoiceDetail import InvoiceDetail
from internal.invoice.models.InvoiceExcelDetail import InvoiceItemDetailSheet, InvoiceSummarySheet


def createInvoiceExcelSheet(invoiceDetails: List[InvoiceDetail]):
    invoiceSummarySheet = InvoiceSummarySheet(invoiceDetails=invoiceDetails)
    invoiceItemDetailSheet = InvoiceItemDetailSheet(invoiceDetails=invoiceDetails)

    invoiceSummarySheetDataframe = polars.DataFrame(invoiceSummarySheet.toDict())
    invoiceItemDetailSheetDataframe = polars.DataFrame(invoiceItemDetailSheet.toDict())

    summaryCount = invoiceSummarySheetDataframe.height

    summaryToItemDetailLink = [
        f"=HYPERLINK(\"#'Item Detail'!A\" & MATCH(A{i + 2}, 'Item Detail'!A:A, 0), \"Jump to Items →\")"
        for i in range(summaryCount)
    ]

    invoiceSummarySheetDataframe = invoiceSummarySheetDataframe.with_columns(
        polars.Series("View Details", summaryToItemDetailLink)
    )

    inmemoryBuffer = io.BytesIO()

    invoiceSummarySheetDataframe.write_excel(
        workbook=inmemoryBuffer, worksheet="Invoice Summary", autofit=True, table_style="Table Style Light 9"
    )
    invoiceItemDetailSheetDataframe.write_excel(
        workbook=inmemoryBuffer, worksheet="Item Detail", autofit=True, table_style="Table Style Light 10"
    )

    inmemoryBuffer.seek(0)
    return inmemoryBuffer.getvalue()
