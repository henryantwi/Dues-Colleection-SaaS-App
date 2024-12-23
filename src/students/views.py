import json
import uuid

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from icecream import ic

from payments.forms import PaymentForm
from payments.models import Payment

from .forms import StudentRegistrationForm
from .models import Department, PendingMomoPayment, Student


def student_registration(request, department_id, is_year_one=False):
    department = get_object_or_404(Department, id=department_id)

    # Check if there's preview data for edit action
    preview_data = request.session.get("registration_preview", {})

    if request.method == "POST":
        # Validate form data
        form_data = {
            "ref_number": request.POST.get("ref_number"),
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "mobile": request.POST.get("mobile"),
            "payment_method": request.POST.get("payment_method"),
        }

        # Check if all fields are filled
        if not all(form_data.values()):
            messages.error(request, "All fields are required.")
            return render(
                request,
                "students/registration.html",
                {
                    "department": department,
                    "is_year_one": is_year_one,
                    "amount": (
                        department.year_one_amount
                        if is_year_one
                        else department.other_years_amount
                    ),
                    **form_data,
                },
            )

        # Check if student already exists
        if Student.objects.filter(ref_number=form_data["ref_number"]).exists():
            messages.error(
                request, "A student with this reference number already exists."
            )
            return render(
                request,
                "students/registration.html",
                {
                    "department": department,
                    "is_year_one": is_year_one,
                    "amount": (
                        department.year_one_amount
                        if is_year_one
                        else department.other_years_amount
                    ),
                    **form_data,
                },
            )

        # Store preview data in session
        preview_data = {
            **form_data,
            "department_id": department.id,
            "department_name": department.name,
            "is_year_one": is_year_one,
            "amount": float(
                department.year_one_amount
                if is_year_one
                else department.other_years_amount
            ),
        }
        request.session["registration_preview"] = preview_data

        # Redirect to preview page
        return redirect("students:registration_preview")

    # GET request
    if "edit" in request.GET:
        # Don't clear preview data if editing
        return render(
            request,
            "students/registration.html",
            {
                "department": department,
                "is_year_one": is_year_one,
                "amount": (
                    department.year_one_amount
                    if is_year_one
                    else department.other_years_amount
                ),
                "ref_number": preview_data.get("ref_number", ""),
                "full_name": preview_data.get("full_name", ""),
                "email": preview_data.get("email", ""),
                "mobile": preview_data.get("mobile", ""),
                "payment_method": preview_data.get("payment_method", ""),
            },
        )

    # Clear preview data for fresh registration
    request.session.pop("registration_preview", None)
    return render(
        request,
        "students/registration.html",
        {
            "department": department,
            "is_year_one": is_year_one,
            "amount": (
                department.year_one_amount
                if is_year_one
                else department.other_years_amount
            ),
        },
    )


def registration_preview(request):
    preview_data = request.session.get("registration_preview")

    if not preview_data:
        messages.error(request, "No registration data found. Please start over.")
        return redirect(
            "students:registration", department_id=1
        )  # Replace with default department ID

    if request.method == "POST":
        if "edit" in request.POST:
            # Keep preview data and redirect back to registration with edit flag
            return redirect(
                f"{reverse('students:registration', kwargs={'department_id': preview_data['department_id']})}?edit=true"
            )

        elif "confirm" in request.POST:
            try:
                department = get_object_or_404(
                    Department, id=preview_data["department_id"]
                )

                # Create payment first
                payment = Payment.objects.create(
                    department=department,
                    method=preview_data["payment_method"],
                    amount=preview_data["amount"]
                )

                # Handle payment method before creating student
                if preview_data["payment_method"] == "Mobile Money":
                    try:
                        headers = {
                            "Authorization": f"Bearer {department.paystack_secret_key}",
                            "Content-Type": "application/json",
                        }
                        data = {
                            "email": preview_data["email"],
                            "amount": int(preview_data["amount"] * 100),
                            "callback_url": request.build_absolute_uri(
                                reverse(
                                    "payments:verify_payment", args=[payment.reference]
                                )
                            ),
                            "reference": payment.reference,
                        }
                        response = requests.post(
                            "https://api.paystack.co/transaction/initialize",
                            headers=headers,
                            data=json.dumps(data),
                        )

                        response_data = response.json()
                        if response.status_code == 200 and response_data.get("status"):
                            # Store in database instead of session
                            PendingMomoPayment.objects.create(
                                ref_number=preview_data["ref_number"],
                                full_name=preview_data["full_name"],
                                email=preview_data["email"],
                                mobile=preview_data["mobile"],
                                department=department,
                                payment=payment
                            )
                            request.session.pop("registration_preview", None)
                            return redirect(response_data["data"]["authorization_url"])
                    except Exception as e:
                        payment.status = "Failed"
                        payment.save()
                        messages.error(request, f"Payment processing error: {str(e)}")
                        # Return to preview page with data intact
                        return render(
                            request, "students/preview.html", {"preview_data": preview_data}
                        )
                elif preview_data["payment_method"] == "Cash":
                    try:
                        # Create student for cash payment
                        student = Student.objects.create(
                            ref_number=preview_data["ref_number"],
                            full_name=preview_data["full_name"],
                            email=preview_data["email"],
                            mobile=preview_data["mobile"],
                            department=department,
                            payment=payment,
                        )
                        # Update payment status for cash
                        payment.status = "Pending"
                        payment.save()
                        
                        # Clear preview data
                        request.session.pop("registration_preview", None)
                        
                        messages.success(request, "Registration successful. Please make cash payment at the department office.")
                        return redirect("students:registration_confirmation", student_id=student.id)
                        
                    except Exception as e:
                        payment.status = "Failed"
                        payment.save()
                        messages.error(request, f"Registration error: {str(e)}")
                        return render(
                            request, "students/preview.html", {"preview_data": preview_data}
                        )
              
            except Exception as e:
                messages.error(request, f"Error processing payment: {str(e)}")
                # Return to preview page with data intact
                return render(
                    request, "students/preview.html", {"preview_data": preview_data}
                )  
        
    return render(request, "students/preview.html", {"preview_data": preview_data})


def registration_confirmation(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(
        request, "students/registration_confirmation.html", {"student": student}
    )
