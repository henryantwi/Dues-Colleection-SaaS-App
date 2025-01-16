from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('departments/', views.department_list, name='department_list'),
    # Put preview and confirmation URLs first
    path('registration/preview/', views.registration_preview, name='registration_preview'),
    path('registration/confirmation/<uuid:student_uuid>/', views.registration_confirmation, name='registration_confirmation'),

    # Then put department-specific URLs
    path('registration/<slug:department_slug>/', views.student_registration, name='registration'),
    path('registration/<slug:department_slug>/year-one/',
         views.student_registration,
         {'is_year_one': True},
         name='registration_year_one'),
]
