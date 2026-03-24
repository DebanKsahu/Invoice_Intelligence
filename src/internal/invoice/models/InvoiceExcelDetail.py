from dataclasses import InitVar, dataclass, field
from datetime import date
from typing import List

from internal.invoice.models.InvoiceDetail import InvoiceDetail


@dataclass
class InvoiceSummarySheet:
    invoiceDetails: InitVar[List[InvoiceDetail]]

    invoiceNumbers: List[str | None] = field(init=False)
    vendorNames: List[str | None] = field(init=False)
    invoiceDates: List[date | None] = field(init=False)
    dueDates: List[date | None] = field(init=False)
    totalAmounts: List[float] = field(init=False)
    paymentStatuses: List[str | None] = field(init=False)

    def __post_init__(self, invoiceDetails: List[InvoiceDetail]):
        self.invoiceNumbers = []
        self.vendorNames = []
        self.invoiceDates = []
        self.dueDates = []
        self.totalAmounts = []
        self.paymentStatuses = []
        for invoiceDetail in invoiceDetails:
            self.invoiceNumbers.append(invoiceDetail.invoiceNumber)
            self.vendorNames.append(invoiceDetail.vendorName)
            self.invoiceDates.append(invoiceDetail.invoiceDate)
            self.dueDates.append(invoiceDetail.dueDate)
            self.totalAmounts.append(invoiceDetail.totalAmount)
            self.paymentStatuses.append(invoiceDetail.paymentStatus)

    def toDict(self):
        return {
            "invoiceNumbers": self.invoiceNumbers,
            "vendorNames": self.vendorNames,
            "invoiceDates": self.invoiceDates,
            "dueDates": self.dueDates,
            "totalAmounts": self.totalAmounts,
            "paymentStatuses": self.paymentStatuses
        }


@dataclass
class InvoiceItemDetailSheet:
    invoiceDetails: InitVar[List[InvoiceDetail]]

    invoiceNumbers: List[str | None] = field(init=False)
    itemDescriptions: List[str | None] = field(init=False)
    itemQuantities: List[float | None] = field(init=False)
    itemUnitPrices: List[float | None] = field(init=False)
    itemTotalPrices: List[float | None] = field(init=False)

    def __post_init__(self, invoiceDetails: List[InvoiceDetail]):
        self.invoiceNumbers = []
        self.itemDescriptions = []
        self.itemQuantities = []
        self.itemUnitPrices = []
        self.itemTotalPrices = []
        for invoiceDetail in invoiceDetails:
            for itemDetail in invoiceDetail.items:
                self.invoiceNumbers.append(invoiceDetail.invoiceNumber)
                self.itemDescriptions.append(itemDetail.description)
                self.itemQuantities.append(itemDetail.quantity)
                self.itemUnitPrices.append(itemDetail.unitPrice)
                self.itemTotalPrices.append(itemDetail.totalPrice)

    def toDict(self):
        return {
            "invoiceNumbers": self.invoiceNumbers,
            "itemDescriptions": self.itemDescriptions,
            "itemQuantities": self.itemQuantities,
            "itemUnitPrices": self.itemUnitPrices,
            "itemTotalPrices": self.itemTotalPrices,
        }
