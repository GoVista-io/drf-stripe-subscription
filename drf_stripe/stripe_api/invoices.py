from django.db.transaction import atomic

from drf_stripe.models import Invoice, StripeUser, Subscription
from .api import stripe_api as stripe
from ..stripe_models.invoice import StripeInvoices


@atomic()
def stripe_api_update_invoices(test_invoices=None, **kwargs):
    """
    Fetch list of Stripe Invoices and updates database.

    :param dict test_invoices:  Response from calling Stripe API: stripe.Invoice.list(). Used for testing.
    """
    if test_invoices is None:
        invoices_data = stripe.Invoice.list(limit=100)
    else:
        invoices_data = test_invoices

    invoices = StripeInvoices(**invoices_data).data

    creation_count = 0
    for invoice in invoices:
        stripe_user = StripeUser.objects.get(customer_id=invoice.customer)
        subscription = None
        if invoice.subscription:
            subscription = Subscription.objects.get(
                subscription_id=invoice.subscription
            )

        invoice_obj, created = Invoice.objects.update_or_create(
            invoice_id=invoice.id,
            defaults={
                "stripe_user": stripe_user,
                "subscription": subscription,
                "auto_advance": invoice.auto_advance,
                "charge": invoice.charge,
                "collection_method": invoice.collection_method,
                "currency": invoice.currency,
                "description": invoice.description,
                "hosted_invoice_url": invoice.hosted_invoice_url,
                "lines": invoice.lines,
                "paid": invoice.paid,
            },
        )
        if created is True:
            creation_count += 1

    print(f"Created {creation_count} new Invoices")
