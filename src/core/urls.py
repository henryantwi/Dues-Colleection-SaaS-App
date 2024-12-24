from django.contrib import admin
from django.urls import include, path

from a_home.views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("students/", include("students.urls")),
    path("administrators/", include("administrators.urls")),
    path("payments/", include("payments.urls")),
]
