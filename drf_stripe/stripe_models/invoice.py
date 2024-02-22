from typing import List, Dict, Optional

from pydantic import BaseModel

from .currency import StripeCurrency
from .price import StripePrice


class StripeInvoiceLineItem(BaseModel):
    """Based on https://stripe.com/docs/api/invoices/line_item"""

    id: str
    amount: int
    currency: StripeCurrency
    description: str = None
    metadata: Dict
    period: Dict
    price: StripePrice
    proration: bool
    quantity: int
    type: str
    discount_amounts: Optional[List[Dict]] = None
    discountable: Optional[bool] = None
    discounts: Optional[List[str]] = None
    invoice_item: Optional[str] = None
    subscription: str


class StripeInvoiceLines(BaseModel):
    """Based on https://stripe.com/docs/api/invoices/object#invoice_object-lines"""

    data: list[StripeInvoiceLineItem]
    has_more: bool
    url: str


class StripeInvoice(BaseModel):
    """Based on https://stripe.com/docs/api/invoices/object"""

    id: str
    auto_advance: Optional[bool] = None
    charge: str = None
    collection_method: Optional[str] = None
    currency: str
    customer: str
    subscription: Optional[str] = None
    description: str = None
    hosted_invoice_url: Optional[str] = None
    lines: Optional[StripeInvoiceLines] = None
    paid: bool

class StripeInvoices(BaseModel):
    """Based on https://stripe.com/docs/api/invoices/list"""

    data: List[StripeInvoice]
    has_more: bool = None
    url: str = None


class StripeInvoiceEventData(BaseModel):
    """Based on https://stripe.com/docs/api/events/object#event_object-data"""

    object: StripeInvoice
    previous_attributes: Optional[StripeInvoice] = None
