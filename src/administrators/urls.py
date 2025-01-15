from django.urls import path

from . import views

app_name = 'administrators'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('search/', views.student_search, name='search'),
    path('student/<str:ref_number>/', views.student_detail, name='student_detail'),
    path('payment/<str:payment_ref>/mark-successful/', 
         views.mark_payment_successful, 
         name='mark_payment_successful'),
    path('students/', views.student_list, name='student_list'),
    path('students/download/', views.download_students_csv, name='download_students'),
    path('student/<str:ref_number>/update-tshirt/', 
         views.update_tshirt_payment, 
         name='update_tshirt_payment'),
]
