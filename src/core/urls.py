from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from a_home.views import home_view

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path("webmaster/", admin.site.urls),
    path("", home_view, name="home"),
    path("students/", include("students.urls")),
    path("administrators/", include("administrators.urls")),
    path("payments/", include("payments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)