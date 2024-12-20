from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "department",
        "method",
        "status",
        "amount",
        "created_at",
    )
    list_filter = ("status", "method", "department", "created_at")
    search_fields = ("reference",)
    readonly_fields = ("reference", "created_at", "updated_at")
