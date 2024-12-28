import uuid

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField

image_storage = (
    MediaCloudinaryStorage()
    if settings.ENVIRONMENT == "production"
    else FileSystemStorage()
)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    year_one_amount = models.DecimalField(max_digits=10, decimal_places=2)
    other_years_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_secret_key = models.CharField(max_length=200)
    paystack_public_key = models.CharField(max_length=200)
    google_app_password = models.CharField(max_length=200)
    image = ResizedImageField(
        size=[600, 600],
        quality=85,
        upload_to="logos/",
        storage=image_storage,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Departments"


class Student(models.Model):
    full_name = models.CharField(max_length=200)
    ref_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    mobile = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\d{10,15}$",
                message="Phone number must be between 10 and 15 digits.",
            )
        ],
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="students"
    )
    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    year_group = models.IntegerField()
    unique_code = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    level = models.IntegerField(default=100)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = str(uuid.uuid4()).upper()[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.ref_number}"

    class Meta:
        ordering = ["-created_at"]


class PendingMomoPayment(models.Model):
    ref_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\d{10,15}$",
                message="Phone number must be between 10 and 15 digits.",
            )
        ],
    )
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    payment = models.OneToOneField("payments.Payment", on_delete=models.CASCADE)
    year_group = models.IntegerField(default=1)
    level = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pending Momo Payment"
        verbose_name_plural = "Pending Momo Payments"
    payment = models.OneToOneField("payments.Payment", on_delete=models.CASCADE)

    year_group = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pending Momo Payment"
        verbose_name_plural = "Pending Momo Payments"
