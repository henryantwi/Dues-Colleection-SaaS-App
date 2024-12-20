from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("create/<int:student_id>/", views.create_payment, name="create_payment"),
    path("verify/<str:reference>/", views.verify_payment, name="verify_payment"),
    path("success/<str:reference>/", views.payment_success, name="payment_success"),
    path("failed/<str:reference>/", views.payment_failed, name="payment_failed"),
    path("pending/<str:reference>/", views.payment_pending, name="payment_pending"),
    path(
        "mark-as-paid/<str:reference>/", views.mark_payment_as_paid, name="mark_as_paid"
    ),
    path("admin/create/", views.create_admin_payment, name="create_admin_payment"),
    path(
        "admin/create/<int:student_id>/",
        views.create_admin_payment,
        name="create_admin_payment_for_student",
    ),
]
