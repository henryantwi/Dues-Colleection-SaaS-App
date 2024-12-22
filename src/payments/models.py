import secrets
import uuid

from django.db import models
from icecream import ic

# Create your models here.


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("Mobile Money", "Mobile Money"),
        ("Cash", "Cash"),
    )

    PAYMENT_STATUS = (
        ("Pending", "Pending"),
        ("Successful", "Successful"),
        ("Failed", "Failed"),
    )

    department = models.ForeignKey(
        "students.Department", on_delete=models.CASCADE, related_name="payments"
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")
    reference = models.CharField(max_length=100, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            # Generate a unique payment reference
            self.reference = f"PAY-{secrets.token_hex(5).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.status}"

    class Meta:
        ordering = ["-created_at"]
