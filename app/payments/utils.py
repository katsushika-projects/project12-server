"""Define functions for payment processing."""

import stripe
from django.conf import settings

from config.exceptions import CreateCheckoutSessionError

from .models import Payment

CLIENT_DOMAIN: str = str(settings.CLIENT_DOMAIN)
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_checkout_session_object(checkout_session_id: str) -> stripe.checkout.Session:
    """
    StripeのCheckoutセッションを取得する関数.

    Args:
        checkout_session_id (str): CheckoutセッションID.

    Returns:
        stripe.checkout.Session: StripeのCheckoutセッションオブジェクト.

    """
    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
    except Exception as e:
        message = f"Stripe Checkoutセッションの取得に失敗しました: {e!s}"
        raise CreateCheckoutSessionError(message) from e

    return session


def create_checkout_session(description: str, name: str, task_id: str, unit_amount: int, email: str | None) -> str:
    """
    StripeのCheckoutセッションを作成し、決済URLを返す関数.

    Args:
        description (str): 商品の説明.
        name (str): 商品名.
        task_id (str): タスクID.
        unit_amount (int): 商品の価格 (単位は円).
        email (str | None, optional): ユーザーのメールアドレス.

    Returns:
        str: 決済ページのURL.

    """
    # Stripeはemailについてblankを受け付けない(Noneは可).
    if not email:
        email = None

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            line_items=[
                {
                    "price_data": {
                        "currency": "jpy",
                        "product_data": {
                            "name": name,
                            "description": description,
                        },
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                },
            ],
            metadata={"task_id": task_id},
            mode="payment",
            payment_intent_data={"capture_method": "manual"},
            success_url=f"{CLIENT_DOMAIN}/dashboard?taskId={task_id}&payment=success",
            cancel_url=f"{CLIENT_DOMAIN}/dashboard?taskId={task_id}&payment=cancel",
        )
    except Exception as e:
        message = f"Stripe Checkoutセッションの作成に失敗しました: {e!s}"
        raise CreateCheckoutSessionError(message) from e

    # PaymentモデルにCheckoutセッションIDを保存
    if not Payment.objects.filter(task_id=task_id).exists():
        payment = Payment(task_id=task_id)
    payment.stripe_checkout_session_id = checkout_session.id
    payment.save()

    return checkout_session.url
