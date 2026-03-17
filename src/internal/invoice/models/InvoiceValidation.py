from pydantic import BaseModel, Field


class InvoiceValidation(BaseModel):
    isInvoice: bool = Field(
        default=False,
        description="True if the text represents an invoice, bill, or financial receipt. False otherwise.",
    )
    confidenceScore: float = Field(
        default=100,
        description="A value between 0.0 and 1.0 indicating how certain you are of the classification.",
    )
