"""Define the Payment model."""

import uuid

from django.db import models

from config.exceptions import CreateCheckoutSessionError


class Payment(models.Model):
    """Define the Payment class."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task = models.OneToOneField(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        related_name="payment",
        verbose_name="タスク",
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        unique=True,
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        """Meta class for Payment."""

        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        """Return a string representation of the Payment object."""
        if self.task:
            return f"Payment {self.id} for Task {self.task.name}"
        return f"Payment {self.id} for Task None"

    def attach_intent_id(self) -> None:
        """Stripe側で存在している payment intentのidをPaymentモデルに保存するメソッド."""
        from .utils import get_checkout_session_object

        session = get_checkout_session_object(self.stripe_checkout_session_id)
        if session.payment_intent:
            self.stripe_payment_intent_id = session.payment_intent
            self.save()
        else:
            message = "Stripe側のpayment intentを取得できませんでした"
            raise CreateCheckoutSessionError(message)

    def payment_status_is_paid(self) -> bool:
        """Checkout sessionの支払いが完了しているかを確認するメソッド."""
        from .utils import get_checkout_session_object

        session = get_checkout_session_object(self.stripe_checkout_session_id)
        return session.payment_status == "paid"

    def stripe_has_payment_intent(self) -> bool:
        """stripe側にpayment_intentが存在しているかを確認するメソッド."""
        from .utils import get_checkout_session_object

        session = get_checkout_session_object(self.stripe_checkout_session_id)
        return bool(session.payment_intent)
