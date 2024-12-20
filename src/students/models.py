from django.db import models
from django.utils.text import slugify
import uuid

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    year_one_amount = models.DecimalField(max_digits=10, decimal_places=2)
    other_years_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_secret_key = models.CharField(max_length=200)
    paystack_public_key = models.CharField(max_length=200)
    google_app_password = models.CharField(max_length=200)

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
    mobile = models.CharField(max_length=15)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    unique_code = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            # Generate a unique 10-character alphanumeric code
            self.unique_code = str(uuid.uuid4()).upper()[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.ref_number}"

    class Meta:
        ordering = ['-created_at']
