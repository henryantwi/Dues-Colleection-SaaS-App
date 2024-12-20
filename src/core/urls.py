from django.contrib import admin
from django.urls import path, include

from a_home.views import home_view
from administrators.views import login_view, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("students/", include("students.urls")),
    path("payments/", include("payments.urls")),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
