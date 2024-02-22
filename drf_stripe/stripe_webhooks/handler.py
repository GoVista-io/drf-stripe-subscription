from pydantic import ValidationError
from rest_framework.request import Request

from drf_stripe.settings import drf_stripe_settings
from drf_stripe.stripe_api.api import stripe_api as stripe
from drf_stripe.stripe_models.event import EventType
from drf_stripe.stripe_models.event import StripeEvent
from .customer_subscription import handle_customer_subscription_event_data
from .price import handle_price_event_data
from .product import handle_product_event_data
from .invoice import handle_invoice_event_data


def handle_stripe_webhook_request(request):
    event = _make_webhook_event_from_request(request)
    handle_webhook_event(event)


def _make_webhook_event_from_request(request: Request):
    """
    Given a Rest Framework request, construct a webhook event.

    :param event: event from Stripe Webhook, defaults to None. Used for test.
    """

    return stripe.Webhook.construct_event(
        payload=request.body,
        sig_header=request.META["HTTP_STRIPE_SIGNATURE"],
        secret=drf_stripe_settings.STRIPE_WEBHOOK_SECRET,
    )


def _handle_event_type_validation_error(err: ValidationError):
    """
    Handle Pydantic ValidationError raised when parsing StripeEvent,
    ignores the error if it is caused by unimplemented event.type;
    Otherwise, raise the error.
    """
    event_type_error = False

    for error in err.errors():
        error_loc = error["loc"]
        if (
            error_loc[0] == "event"
            and error.get("ctx", {}).get("discriminator_key", {}) == "type"
        ):
            event_type_error = True
            break

    if event_type_error is False:
        raise err


def handle_webhook_event(event):
    """Perform actions given Stripe Webhook event data."""

    try:
        e = StripeEvent(event=event)
    except ValidationError as err:
        _handle_event_type_validation_error(err)
        return

    event_type = e.event.type

    # Subscription events
    if event_type in [
        EventType.CUSTOMER_SUBSCRIPTION_CREATED,
        EventType.CUSTOMER_SUBSCRIPTION_UPDATED,
        EventType.CUSTOMER_SUBSCRIPTION_DELETED,
    ]:
        handle_customer_subscription_event_data(e.event.data)

    # Product events
    elif event_type in [
        EventType.PRODUCT_CREATED,
        EventType.PRODUCT_UPDATED,
        EventType.PRODUCT_DELETED,
    ]:
        handle_product_event_data(e.event.data)

    # Price events
    elif event_type in [
        EventType.PRICE_CREATED,
        EventType.PRICE_UPDATED,
        EventType.PRICE_DELETED,
    ]:
        handle_price_event_data(e.event.data)

    # Invoice events
    elif event_type in [
        EventType.INVOICE_CREATED,
        EventType.INVOICE_PAID,
        EventType.INVOICE_FINALIZED,
        EventType.INVOICE_UPDATED,
    ]:
        handle_invoice_event_data(e.event.data)
