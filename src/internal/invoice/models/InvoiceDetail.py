from datetime import date
from typing import List

from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    description: str | None = Field(
        default=None, description="The name or description of the product or service."
    )
    quantity: float | None = Field(
        None, description="The quantity of the item purchased. Use a float (e.g., 1.0, 2.5)."
    )
    unitPrice: float | None = Field(None, description="The price of a single unit, without currency symbols.")
    totalPrice: float | None = Field(
        None, description="The total cost for this item, without currency symbols."
    )


class InvoiceTexBreakdown(BaseModel):
    taxType: str | None = Field(
        default=None, description="The type of tax applied (e.g., GST, VAT, State Tax, SGST, CGST)."
    )
    taxAmount: float = Field(default=0, description="The amount of tax charged, without currency symbols.")
    taxRate: float = Field(
        default=0, description="The percentage rate of the tax if mentioned (e.g., 10, 18.5)."
    )


class InvoiceDetail(BaseModel):
    vendorName: str | None = Field(
        default=None, description="The name of the company or person issuing the invoice."
    )
    invoiceNumber: str | None = Field(
        default=None, description="The unique identifier for the invoice (letters and numbers)."
    )
    invoiceDate: date | None = Field(
        default=None, description="The date the invoice was issued. Format as YYYY-MM-DD."
    )
    dueDate: date | None = Field(
        default=None, description="The date the payment is due. Format as YYYY-MM-DD."
    )
    totalAmount: float = Field(
        default=0, description="The final total amount due, including all taxes. No currency symbols."
    )
    items: List[InvoiceItem] = Field(
        default_factory=list, description="A list of all individual items purchased."
    )
    taxBreakdown: List[InvoiceTexBreakdown] = Field(
        default_factory=list, description="A breakdown of the taxes applied to the invoice, if present."
    )
    paymentStatus: str | None = Field(
        default=None, description="The current status of the payment (e.g., Paid, Unpaid, Pending, Overdue)."
    )
