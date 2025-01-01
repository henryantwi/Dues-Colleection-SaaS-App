import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from icecream import ic

# Configure logger
logger = logging.getLogger(__name__)


# Create your views here.
def home_view(request):
    return render(request, "home.html")


def terms_view(request):
    return render(request, "pages/terms.html")


def privacy_view(request):
    return render(request, "pages/privacy.html")


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        message = request.POST.get("message")

        if name and email and mobile and message:
            try:
                # Prepare email content
                email_context = {
                    "name": name,
                    "email": email,
                    "mobile": mobile,
                    "message": message,
                }

                # Render email templates
                email_subject = f"Contact Form Message from {name}"
                email_body = render_to_string(
                    "emails/contact_email.html", email_context
                )

                # Send email
                ic(settings.CONTACT_EMAIL)
                ic(settings.DEFAULT_FROM_EMAIL)
                send_mail(
                    subject=email_subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[
                        "henryantwi191@gmail.com",
                        "evansankomah640@gmail.com",
                        "antwi.henry@outlook.com",
                    ],
                    html_message=email_body,
                    fail_silently=False,
                )

                messages.success(
                    request, "Thank you for your message! We'll get back to you soon."
                )
                return redirect("contact")

            except Exception as e:
                logger.error(
                    f"Error sending contact form email: {str(e)}", exc_info=True
                )
                if settings.DEBUG:
                    error_message = f"Error: {str(e)}"
                else:
                    error_message = "Sorry, there was an error sending your message. Please try again later."
                messages.error(request, error_message)

                # Return with form data to preserve user input
                return render(
                    request,
                    "pages/contact.html",
                    {
                        "form_data": {
                            "name": name,
                            "email": email,
                            "mobile": mobile,
                            "message": message,
                        }
                    },
                )
        else:
            messages.error(request, "Please fill in all fields.")
            # Return with partial form data
            return render(
                request,
                "pages/contact.html",
                {
                    "form_data": {
                        "name": name or "",
                        "email": email or "",
                        "mobile": mobile or "",
                        "message": message or "",
                    }
                },
            )

    return render(request, "pages/contact.html")
