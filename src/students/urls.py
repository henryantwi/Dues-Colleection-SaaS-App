from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('registration/<int:department_id>/', views.student_registration, name='registration'),
    path('registration/<int:department_id>/year-one/', 
         views.student_registration, 
         {'is_year_one': True}, 
         name='registration_year_one'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('search/', views.student_search, name='search'),  # Adding back the search URL
    path('registration/preview/', views.registration_preview, name='registration_preview'),
    path('registration/confirmation/<int:student_id>/', views.registration_confirmation, name='registration_confirmation'),
]
