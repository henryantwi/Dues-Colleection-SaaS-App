from django.urls import path

from . import views

app_name = 'administrators'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('search/', views.student_search, name='search'),
]
