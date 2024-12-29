import json

import requests
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from icecream import ic

from payments.models import Payment

from .models import Department, PendingMomoPayment, Student

# ic.disable()


def _clear_registration_session(request):
    """Helper function to clear all registration-related session data"""
    keys_to_clear = ["registration_preview", "registration_return_url"]
    for key in keys_to_clear:
        request.session.pop(key, None)


def student_registration(request, department_slug, is_year_one=False):
    department = get_object_or_404(Department, slug=department_slug)

    # Store the current path for return redirect
    request.session["registration_return_url"] = request.path

    # Get preview data from session
    preview_data = request.session.get("registration_preview", {})
    
    if request.method == "POST":
        # Validate form data
        form_data = {
            "ref_number": request.POST.get("ref_number"),
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "mobile": request.POST.get("mobile"),
            "payment_method": request.POST.get("payment_method"),
            "level": request.POST.get("level") if not is_year_one else "100",
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

    # Check if we're coming back to edit
    initial_data = {}
    if (preview_data):
        initial_data = {
            "ref_number": preview_data.get("ref_number", ""),
            "full_name": preview_data.get("full_name", ""),
            "email": preview_data.get("email", ""),
            "mobile": preview_data.get("mobile", ""),
            "payment_method": preview_data.get("payment_method", ""),
            "level": preview_data.get("level", ""),  # Add this line
        }

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
            **initial_data,  # This will populate the form fields with previous data
        },
    )


def registration_preview(request):
    preview_data = request.session.get("registration_preview")

    if not preview_data:
        messages.error(request, "No registration data found. Please start over.")
        # Get first department as fallback
        department = Department.objects.first()
        return redirect("students:registration", department_slug=department.slug)

    if request.method == "POST":
        if "edit" in request.POST:
            # Keep the preview data in session when going back to edit
            return_url = request.POST.get("return_url", "")
            if not return_url:
                department = get_object_or_404(Department, id=preview_data["department_id"])
                return redirect("students:registration", department_slug=department.slug)
            return redirect(return_url)

        elif "confirm" in request.POST:
            try:
                department = get_object_or_404(
                    Department, id=preview_data["department_id"]
                )

                # Create payment first
                payment = Payment.objects.create(
                    department=department,
                    method=preview_data["payment_method"],
                    amount=preview_data["amount"],
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
                                payment=payment,
                                year_group=1 if preview_data["is_year_one"] else 2,
                                level=int(preview_data["level"]),
                            )
                            # Clear all registration session data after successful processing
                            request.session.pop("registration_preview", None)
                            request.session.pop("registration_return_url", None)
                            return redirect(response_data["data"]["authorization_url"])
                    except Exception as e:
                        ic(e)
                        payment.status = "Failed"
                        payment.save()
                        messages.error(request, f"Payment processing error: {str(e)}")
                        # Return to preview page with data intact
                        return render(
                            request,
                            "students/preview.html",
                            {"preview_data": preview_data},
                        )
                elif preview_data["payment_method"] == "Cash":
                    messages.error(request, "Cash payment method is currently unavailable. Please use Mobile Money.")
                    return render(
                        request,
                        "students/preview.html",
                        {"preview_data": preview_data},
                    )

            except Exception as e:
                ic(e)
                messages.error(request, f"Error processing payment: {str(e)}")
                # Return to preview page with data intact
                return render(
                    request, "students/preview.html", {"preview_data": preview_data}
                )

    # Add the current path to the preview data
    preview_data["return_url"] = request.session.get("registration_return_url")

    return render(request, "students/preview.html", {"preview_data": preview_data})


def registration_confirmation(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(
        request, "students/registration_confirmation.html", {"student": student}
    )


def department_list(request):
    departments = Department.objects.all()
    return render(request, "students/department_list.html", {"departments": departments})
    return render(request, "students/department_list.html", {"departments": departments})



