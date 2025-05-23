from django.db import models
from django.conf import settings
from django.utils import timezone
from marketplace.models import Order  # Make sure this is the correct import
import uuid

# --- Payment Model ---
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment_detail',
        null=True,
        blank=True,
        verbose_name="Order"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name="Payment Method"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount Paid"
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Transaction ID"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Paid"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verified"
    )
    network = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Mobile Network"
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Phone Number"
    )
    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Payment Status"
    )

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']

    def __str__(self):
        if self.order:
            return f"Payment {self.transaction_id} for Order #{self.order.id}"
        return f"Payment {self.transaction_id}"

    def is_payment_verified(self):
        """Check if the payment is verified."""
        return self.is_verified

    def is_payment_successful(self):
        """Check if the payment is verified and successful."""
        return self.is_verified and self.status == "successful"

class ReceiptLog(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='receipt_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    receipt_number = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4  # Automatically generate a unique identifier
    )
    created_at = models.DateTimeField(default=timezone.now)

    # Optional metadata
    generated_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    transaction_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Order {self.order.id}"
