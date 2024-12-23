from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import EmailAuthenticationForm
from django.contrib.auth.decorators import login_required

from students.models import Student
from payments.models import Payment
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.urls import reverse

from django.db.models import Sum, Count, Q


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'administrators/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def student_search(request):
    query = request.GET.get("q", "")
    if query:
        students = Student.objects.filter(
            Q(ref_number__icontains=query)
            | Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(payment__reference__icontains=query)
            | Q(unique_code__icontains=query)
        ).select_related("department", "payment")

        # check if students are in the same department as the admin
        if not request.user.is_superuser:
            students = students.filter(department=request.user.department)
    else:
        students = Student.objects.none()

    return render(
        request, "administrators/search.html", {"students": students, "query": query}
    )


@login_required
def admin_dashboard(request):
    # Check if user is a department admin
    try:
        department_admin = request.user.departmentadmin
        if not department_admin.is_active:
            raise PermissionDenied
        department = department_admin.department
    except:
        if not request.user.is_superuser:
            raise PermissionDenied
        department = None

    # Get department statistics
    students_query = Student.objects.all()
    if department:
        students_query = students_query.filter(department=department)

    # Get payments for students in this department
    payments_query = Payment.objects.filter(status="Successful")
    if department:
        payments_query = payments_query.filter(department=department)

    total_amount = payments_query.aggregate(total=Sum("amount"))["total"] or 0
    total_students = students_query.count()
    paid_students = students_query.filter(payment__status="Successful").count()
    pending_payments = Payment.objects.filter(
        status="Pending", department=department if department else None
    ).count()

    # Get recent payments
    recent_payments = (
        Payment.objects.filter(department=department if department else None)
        .select_related("department")
        .prefetch_related("students")
        .order_by("-created_at")[:5]
    )

    return render(
        request,
        "administrators/admin_dashboard.html",
        {
            "department": department,
            "total_amount": total_amount,
            "total_students": total_students,
            "paid_students": paid_students,
            "pending_payments": pending_payments,
            "recent_payments": recent_payments,
        },
    )
