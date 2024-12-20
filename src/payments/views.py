from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Payment
from .forms import PaymentForm
from students.models import Student
import requests
import json 

def create_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    department = student.department
    
    # Determine amount based on student's department and year
    amount = department.year_one_amount if student.ref_number.startswith('1') else department.other_years_amount
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.department = department
            payment.amount = amount
            payment.save()
            
            student.payment = payment
            student.save()
            
            if payment.method == 'Mobile Money':
                # Initialize Paystack payment
                try:
                    headers = {
                        'Authorization': f'Bearer {department.paystack_secret_key}',
                        'Content-Type': 'application/json',
                    }
                    data = {
                        'email': student.email,
                        'amount': int(amount * 100),  # Convert to kobo
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
                    
                    if response.status_code == 200:
                        return redirect(response.json()['data']['authorization_url'])
                    else:
                        messages.error(request, 'Failed to initialize payment. Please try again.')
                except Exception as e:
                    messages.error(request, 'An error occurred. Please try again.')
                    payment.status = 'Failed'
                    payment.save()
            else:
                # For cash payments
                messages.success(request, f'Please note your payment reference: {payment.reference}')
                messages.info(request, 'Take this reference to the registration desk to complete your payment.')
                return redirect('payments:payment_pending', reference=payment.reference)
    else:
        form = PaymentForm()
    
    return render(request, 'payments/create_payment.html', {
        'form': form,
        'student': student,
        'amount': amount
    })

def verify_payment(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    department = payment.department
    
    if payment.status == 'Successful':
        return redirect('payments:payment_success', reference=reference)
    
    try:
        headers = {
            'Authorization': f'Bearer {department.paystack_secret_key}',
        }
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data['data']['status'] == 'success':
                payment.status = 'Successful'
                payment.save()
                
                # Send email/SMS confirmation
                try:
                    send_payment_confirmation(payment)
                except:
                    pass  # Don't fail if notification fails
                
                return redirect('payments:payment_success', reference=reference)
    except:
        pass
    
    payment.status = 'Failed'
    payment.save()
    messages.error(request, 'Payment verification failed.')
    return redirect('payments:payment_failed', reference=reference)

@login_required
def mark_payment_as_paid(request, reference):
    user_profile = request.user.profile
    payment = get_object_or_404(Payment, reference=reference)
    
    if not user_profile.is_department_admin and not request.user.is_superuser:
        raise PermissionDenied
    
    if user_profile.is_department_admin and payment.department != user_profile.department:
        raise PermissionDenied
    
    if payment.method == 'Cash' and payment.status == 'Pending':
        payment.status = 'Successful'
        payment.save()
        
        # Send email confirmation
        try:
            send_payment_confirmation(payment)
        except:
            pass
        
        messages.success(request, 'Payment has been marked as successful.')
    else:
        messages.error(request, 'Invalid payment status or method.')
    
    return redirect('students:admin_dashboard')

@login_required
def create_admin_payment(request):
    try:
        department_admin = request.user.departmentadmin
        if not department_admin.is_active:
            raise PermissionDenied
        department = department_admin.department
    except:
        if not request.user.is_superuser:
            raise PermissionDenied
        department = None

    if request.method == 'POST':
        # Get student info from form
        ref_number = request.POST.get('ref_number')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        payment_method = request.POST.get('payment_method')
        amount_type = request.POST.get('amount_type')
        custom_amount = request.POST.get('custom_amount')

        # Validate student info
        if not all([ref_number, full_name, email, mobile, payment_method, amount_type]):
            messages.error(request, 'All fields are required.')
            return render(request, 'payments/create_admin_payment.html', {
                'department': department,
                'ref_number': ref_number,
                'full_name': full_name,
                'email': email,
                'mobile': mobile,
                'payment_method': payment_method,
                'amount_type': amount_type,
                'custom_amount': custom_amount
            })

        # Check if student already exists
        student = Student.objects.filter(ref_number=ref_number).first()
        if student:
            if student.payment and student.payment.status == 'Successful':
                messages.error(request, 'This student has already paid.')
                return redirect('students:admin_dashboard')
        else:
            # Create new student
            student = Student(
                ref_number=ref_number,
                full_name=full_name,
                email=email,
                mobile=mobile,
                department=department
            )
            student.save()

        # Calculate amount based on selection
        if amount_type == 'custom':
            if not custom_amount:
                messages.error(request, 'Custom amount is required.')
                return render(request, 'payments/create_admin_payment.html', {
                    'department': department,
                    'ref_number': ref_number,
                    'full_name': full_name,
                    'email': email,
                    'mobile': mobile,
                    'payment_method': payment_method,
                    'amount_type': amount_type
                })
            amount = float(custom_amount)
        else:
            amount = (
                department.year_one_amount if amount_type == 'year_one'
                else department.other_years_amount
            )

        # Create payment
        payment = Payment.objects.create(
            department=department,
            method=payment_method,
            amount=amount
        )

        student.payment = payment
        student.save()

        if payment_method == 'Cash':
            payment.status = 'Successful'
            payment.save()
            messages.success(request, f'Cash payment of GH₵{amount} recorded successfully for {student.full_name}')
            return redirect('students:admin_dashboard')
        else:
            # For Mobile Money, redirect to Paystack
            try:
                headers = {
                    'Authorization': f'Bearer {department.paystack_secret_key}',
                    'Content-Type': 'application/json',
                }
                data = {
                    'email': student.email,
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
                
                if response.status_code == 200:
                    return redirect(response.json()['data']['authorization_url'])
                else:
                    messages.error(request, 'Failed to initialize payment. Please try again.')
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
                payment.status = 'Failed'
                payment.save()

    return render(request, 'payments/create_admin_payment.html', {
        'department': department
    })

def payment_success(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    return render(request, 'payments/success.html', {'payment': payment})

def payment_failed(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    return render(request, 'payments/failed.html', {'payment': payment})

def payment_pending(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    return render(request, 'payments/pending.html', {'payment': payment})

def send_payment_confirmation(payment):
    student = payment.students.first()
    if not student:
        return
    
    # Send email confirmation
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    context = {
        'student': student,
        'payment': payment,
    }
    
    html_message = render_to_string('payments/email/confirmation.html', context)
    
    send_mail(
        subject='Payment Confirmation',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student.email],
        html_message=html_message,
    )
