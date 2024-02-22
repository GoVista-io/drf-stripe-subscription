from drf_stripe.models import Invoice, StripeUser, Subscription
from drf_stripe.stripe_models.invoice import StripeInvoiceEventData


def handle_product_event_data(data: StripeInvoiceEventData):
    invoice_id = data.object.id
    auto_advance = data.object.auto_advance
    charge = data.object.charge
    collection_method = data.object.collection_method
    currency = data.object.currency
    customer = data.object.customer
    description = data.object.description
    hosted_invoice_url = data.object.hosted_invoice_url
    paid = data.object.paid

    lines = data.object.lines

    stripe_user = StripeUser.objects.get(customer_id=customer)
    subscription = None
    if data.object.subscription:
        subscription = Subscription.objects.get(
            subscription_id=data.object.subscription
        )
    invoice, created = Invoice.objects.update_or_create(
        invoice_id=invoice_id,
        defaults={
            "stripe_user": stripe_user,
            "subscription": subscription,
            "auto_advance": auto_advance,
            "charge": charge,
            "collection_method": collection_method,
            "currency": currency,
            "description": description,
            "hosted_invoice_url": hosted_invoice_url,
            "paid": paid,
        },
    )
