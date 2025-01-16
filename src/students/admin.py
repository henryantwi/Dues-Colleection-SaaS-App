from django.contrib import admin

from .models import Department, PendingMomoPayment, Student


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "year_one_amount", "other_years_amount", "is_active", "service_charge", "tshirt_included", "tshirt_price")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    # list_editable = ["service_charge", "tshirt_included", "tshirt_price"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "ref_number",
        "department",
        "unique_code",
        "created_at",
    )
    list_filter = ("department", "created_at")
    search_fields = ("full_name", "ref_number", "unique_code", "email")
    readonly_fields = ("unique_code", "created_at", "updated_at")


@admin.register(PendingMomoPayment)
class PendingMomoPaymentAdmin(admin.ModelAdmin):
    list_display = ("ref_number", "full_name", "email", "mobile", "department", "payment", "created_at")
    list_filter = ("department", "created_at")
    search_fields = ("ref_number", "full_name", "email", "mobile")
    readonly_fields = ("created_at",)
