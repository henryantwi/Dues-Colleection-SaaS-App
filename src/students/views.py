import json

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from icecream import ic

from payments.models import Payment

from .models import Department, PendingMomoPayment, Student


def _clear_registration_session(request):
    """Helper function to clear all registration-related session data"""
    keys_to_clear = ["registration_preview", "registration_return_url"]
    for key in keys_to_clear:
        request.session.pop(key, None)


def calculate_total_amount(department, form_data, is_year_one, service_charge):
    base_amount = float(
        department.year_one_amount if is_year_one else department.other_years_amount
    )
    total = base_amount + service_charge

    if is_year_one and department.tshirt_included:
        tshirt_option = form_data.get("tshirt_option")
        if tshirt_option == "full":
            total += float(department.tshirt_price)
        elif tshirt_option == "partial":
            total += float(department.tshirt_price) / 2
        # No addition for 'none' option

    return total


def calculate_tshirt_amount(department, tshirt_option):
    if not department.tshirt_included or tshirt_option == "none":
        return 0

    if tshirt_option == "full":
        return float(department.tshirt_price)
    elif tshirt_option == "partial":
        return float(department.tshirt_price) / 2

    return 0


def student_registration(request, department_slug, is_year_one=False):
    department = get_object_or_404(Department, slug=department_slug, is_active=True)
    SERVICE_CHARGE = float(department.service_charge)

    # Store the current path for return redirect
    request.session["registration_return_url"] = request.path
    ic(request.session["registration_return_url"])

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
            "tshirt_option": (
                request.POST.get("tshirt_option")
                if is_year_one and department.tshirt_included
                else "none"
            ),
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
                    "service_charge": SERVICE_CHARGE,  # Add this line
                    "dues_amount": (  # Add this line
                        department.year_one_amount
                        if is_year_one
                        else department.other_years_amount
                    ),
                    "amount": (  # Update this line
                        float(
                            department.year_one_amount
                            if is_year_one
                            else department.other_years_amount
                        )
                        + SERVICE_CHARGE
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
                    "service_charge": SERVICE_CHARGE,  # Add this line
                    "dues_amount": (  # Add this line
                        department.year_one_amount
                        if is_year_one
                        else department.other_years_amount
                    ),
                    "amount": (  # Update this line
                        float(
                            department.year_one_amount
                            if is_year_one
                            else department.other_years_amount
                        )
                        + SERVICE_CHARGE
                    ),
                    **form_data,
                },
            )

        # Calculate T-shirt amount
        tshirt_amount = calculate_tshirt_amount(department, form_data["tshirt_option"])
        total_amount = calculate_total_amount(
            department, form_data, is_year_one, SERVICE_CHARGE
        )

        # Store preview data in session
        preview_data = {
            **form_data,
            "department_id": department.id,
            "department_name": department.name,
            "is_year_one": is_year_one,
            "service_charge": SERVICE_CHARGE,
            "dues_amount": float(
                department.year_one_amount
                if is_year_one
                else department.other_years_amount
            ),
            "tshirt_price": (
                float(department.tshirt_price) if department.tshirt_included else 0
            ),
            "tshirt_included": department.tshirt_included,
            "tshirt_amount": tshirt_amount,
            "amount": total_amount,
        }
        request.session["registration_preview"] = preview_data

        # Redirect to preview page
        return redirect("students:registration_preview")

    # Check if we're coming back to edit
    initial_data = {}
    if preview_data:
        initial_data = {
            "ref_number": preview_data.get("ref_number", ""),
            "full_name": preview_data.get("full_name", ""),
            "email": preview_data.get("email", ""),
            "mobile": preview_data.get("mobile", ""),
            "payment_method": preview_data.get("payment_method", ""),
            "level": preview_data.get("level", ""),
            "tshirt_option": preview_data.get(
                "tshirt_option", "full"
            ),
        }

    return render(
        request,
        "students/registration.html",
        {
            "department": department,
            "is_year_one": is_year_one,
            "service_charge": SERVICE_CHARGE,
            "dues_amount": (
                department.year_one_amount
                if is_year_one
                else department.other_years_amount
            ),
            "tshirt_price": float(department.tshirt_price),
            "tshirt_option": preview_data.get(
                "tshirt_option", "full"
            ),
            "amount": calculate_total_amount(
                department, initial_data, is_year_one, SERVICE_CHARGE
            ),  # Update to use initial_data
            **initial_data,  # This will populate the form fields with previous data
        },
    )


def registration_preview(request):
    preview_data = request.session.get("registration_preview")

    if not preview_data:
        messages.error(request, "No registration data found. Please start over.")
        return redirect("students:department_list")

    if request.method == "POST":
        if "edit" in request.POST:
            # Get the return URL from the form
            return_url = request.POST.get("return_url")

            # If no return URL, get department from preview data and redirect to registration
            if not return_url:
                department = get_object_or_404(
                    Department, id=preview_data["department_id"]
                )
                return redirect(
                    "students:registration", department_slug=department.slug
                )

            # Redirect to the stored return URL
            return redirect(return_url)

        elif "confirm" in request.POST:
            try:
                department = get_object_or_404(
                    Department, id=preview_data["department_id"]
                )
                payment = Payment.objects.create(
                    department=department,
                    method=preview_data["payment_method"],
                    amount=preview_data["amount"],
                )

                if preview_data["payment_method"] == "Mobile Money":

                    try:
                        headers = {
                            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
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
                            try:
                                # Check for existing pending payment
                                existing_pending = PendingMomoPayment.objects.filter(
                                    ref_number=preview_data["ref_number"]
                                ).first()

                                if existing_pending:
                                    # Update existing record with new payment
                                    existing_pending.payment = payment
                                    existing_pending.full_name = preview_data[
                                        "full_name"
                                    ]
                                    existing_pending.email = preview_data["email"]
                                    existing_pending.mobile = preview_data["mobile"]
                                    existing_pending.level = int(preview_data["level"])
                                    existing_pending.year_group = (
                                        1 if preview_data["is_year_one"] else 2
                                    )
                                    existing_pending.save()
                                else:
                                    # Create new pending payment record
                                    PendingMomoPayment.objects.create(
                                        ref_number=preview_data["ref_number"],
                                        full_name=preview_data["full_name"],
                                        email=preview_data["email"],
                                        mobile=preview_data["mobile"],
                                        department=department,
                                        payment=payment,
                                        year_group=(
                                            1 if preview_data["is_year_one"] else 2
                                        ),
                                        level=int(preview_data["level"]),
                                    )

                                # Don't clear the session data yet - only store the payment reference
                                request.session["pending_payment_ref"] = (
                                    payment.reference
                                )
                                return redirect(
                                    response_data["data"]["authorization_url"]
                                )

                            except Exception as e:
                                payment.status = "Failed"
                                payment.save()
                                messages.error(
                                    request, f"Error processing payment: {str(e)}"
                                )
                                return render(
                                    request,
                                    "students/preview.html",
                                    {"preview_data": preview_data},
                                )
                    except Exception as e:
                        payment.status = "Failed"
                        payment.save()
                        messages.error(
                            request, f"Payment initialization error: {str(e)}"
                        )
                        return render(
                            request,
                            "students/preview.html",
                            {"preview_data": preview_data},
                        )

                elif preview_data["payment_method"] == "Cash":
                    # Create student record
                    student = Student.objects.create(
                        ref_number=preview_data["ref_number"],
                        full_name=preview_data["full_name"],
                        email=preview_data["email"],
                        mobile=preview_data["mobile"],
                        department=department,
                        payment=payment,
                        year_group=1 if preview_data["is_year_one"] else 2,
                        level=int(preview_data["level"]),
                        tshirt_option=preview_data.get("tshirt_option", "none")
                    )
                    
                    # Mark payment as successful
                    payment.status = "Pending"
                    payment.save()
                    
                    # Clear all session data
                    _clear_registration_session(request)
                    
                    # # Add success message
                    # messages.warning(request,
                    #     "Registration successful! Please proceed to the registration desk with your unique code to complete the process."
                    # )
                    
                    # Redirect to confirmation page
                    return redirect("students:registration_confirmation", student_uuid=student.uuid)

            except Exception as e:
                messages.error(request, f"Error processing payment: {str(e)}")
                return render(
                    request, "students/preview.html", {"preview_data": preview_data}
                )

    # Check if there's a pending payment reference in session
    pending_ref = request.session.get("pending_payment_ref")
    if pending_ref:
        try:
            # Check if payment was successful
            payment = Payment.objects.get(reference=pending_ref)
            if payment.status == "Successful":
                # Clear all session data if payment was successful
                _clear_registration_session(request)
                request.session.pop("pending_payment_ref", None)
            elif payment.status == "Failed":
                # Clear only the payment reference if failed
                request.session.pop("pending_payment_ref", None)
        except Payment.DoesNotExist:
            # Clear the payment reference if payment doesn't exist
            request.session.pop("pending_payment_ref", None)

    # Add the current path to the preview data
    preview_data["return_url"] = request.session.get("registration_return_url")

    return render(request, "students/preview.html", {"preview_data": preview_data})


def registration_confirmation(request, student_uuid):
    student = get_object_or_404(Student, uuid=student_uuid)
    return render(
        request, "students/registration_confirmation.html", {"student": student}
    )


def department_list(request):
    departments = Department.objects.filter(is_active=True)
    return render(
        request, "students/department_list.html", {"departments": departments}
    )
