from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count
from .models import Department, Student
from .forms import StudentRegistrationForm
from payments.forms import PaymentForm
from payments.models import Payment
from django.db.models import Q
import requests
import json
import uuid

def student_registration(request, department_id, is_year_one=False):
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            ref_number = request.POST.get('ref_number')
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            payment_method = request.POST.get('payment_method')

            # Validate form data
            if not all([ref_number, full_name, email, mobile, payment_method]):
                messages.error(request, 'All fields are required.')
                return render(request, 'students/registration.html', {
                    'department': department,
                    'is_year_one': is_year_one,
                    'amount': department.year_one_amount if is_year_one else department.other_years_amount,
                    'ref_number': ref_number,
                    'full_name': full_name,
                    'email': email,
                    'mobile': mobile,
                    'payment_method': payment_method
                })

            # Check if student already exists
            if Student.objects.filter(ref_number=ref_number).exists():
                messages.error(request, 'A student with this reference number already exists.')
                return render(request, 'students/registration.html', {
                    'department': department,
                    'is_year_one': is_year_one,
                    'amount': department.year_one_amount if is_year_one else department.other_years_amount,
                    'ref_number': ref_number,
                    'full_name': full_name,
                    'email': email,
                    'mobile': mobile,
                    'payment_method': payment_method
                })

            # Calculate amount
            amount = department.year_one_amount if is_year_one else department.other_years_amount

            # Create payment first
            payment = Payment.objects.create(
                department=department,
                method=payment_method,
                amount=amount,
                status='Pending'
            )

            # Create student
            student = Student.objects.create(
                ref_number=ref_number,
                full_name=full_name,
                email=email,
                mobile=mobile,
                department=department,
                payment=payment  # Link payment directly during creation
            )

            # Handle payment method
            if payment_method == 'Cash':
                return render(request, 'students/registration_confirmation.html', {
                    'student': student,
                    'payment': payment
                })
            else:  # Mobile Money
                try:
                    headers = {
                        'Authorization': f'Bearer {department.paystack_secret_key}',
                        'Content-Type': 'application/json',
                    }
                    data = {
                        'email': email,
                        'amount': int(amount * 100),  # Convert to pesewas
                        'callback_url': request.build_absolute_uri(
                            reverse('payments:verify_payment', args=[payment.reference])
                        ),
                        'reference': payment.reference,
                    }
                    response = requests.post(
                        'https://api.paystack.co/transaction/initialize',
                        headers=headers,
                        data=json.dumps(data)
                    )
                    
                    response_data = response.json()
                    if response.status_code == 200 and response_data.get('status'):
                        return redirect(response_data['data']['authorization_url'])
                    else:
                        payment.status = 'Failed'
                        payment.save()
                        messages.error(request, 'Failed to initialize payment. Please try again.')
                        return render(request, 'students/registration_confirmation.html', {
                            'student': student,
                            'payment': payment
                        })
                except Exception as e:
                    payment.status = 'Failed'
                    payment.save()
                    messages.error(request, f'Payment processing error: {str(e)}')
                    return render(request, 'students/registration_confirmation.html', {
                        'student': student,
                        'payment': payment
                    })

        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
            return render(request, 'students/registration.html', {
                'department': department,
                'is_year_one': is_year_one,
                'amount': department.year_one_amount if is_year_one else department.other_years_amount,
                'ref_number': ref_number if 'ref_number' in locals() else '',
                'full_name': full_name if 'full_name' in locals() else '',
                'email': email if 'email' in locals() else '',
                'mobile': mobile if 'mobile' in locals() else '',
                'payment_method': payment_method if 'payment_method' in locals() else ''
            })

    # GET request
    return render(request, 'students/registration.html', {
        'department': department,
        'is_year_one': is_year_one,
        'amount': department.year_one_amount if is_year_one else department.other_years_amount
    })

def registration_preview(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    preview_data = request.session.get('student_preview', {})
    
    if request.method == 'POST':
        if 'edit' in request.POST:
            return redirect('students:registration', 
                          department_slug=student.department.slug,
                          is_year_one=student.ref_number.startswith('1'))
        elif 'confirm' in request.POST:
            return redirect('payments:create_payment', student_id=student.id)
    
    return render(request, 'students/preview.html', {
        'student': student,
        'preview_data': preview_data
    })

@login_required
def student_search(request):
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(ref_number__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email__icontains=query)
        ).select_related('department', 'payment')
    else:
        students = Student.objects.none()

    return render(request, 'students/search.html', {
        'students': students,
        'query': query
    })

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
    payments_query = Payment.objects.filter(status='Successful')
    if department:
        payments_query = payments_query.filter(department=department)
    
    total_amount = payments_query.aggregate(total=Sum('amount'))['total'] or 0
    total_students = students_query.count()
    paid_students = students_query.filter(payment__status='Successful').count()
    pending_payments = Payment.objects.filter(
        status='Pending',
        department=department if department else None
    ).count()
    
    # Get recent payments
    recent_payments = Payment.objects.filter(
        department=department if department else None
    ).select_related('department').prefetch_related('students').order_by('-created_at')[:5]
    
    return render(request, 'students/admin_dashboard.html', {
        'department': department,
        'total_amount': total_amount,
        'total_students': total_students,
        'paid_students': paid_students,
        'pending_payments': pending_payments,
        'recent_payments': recent_payments
    })
