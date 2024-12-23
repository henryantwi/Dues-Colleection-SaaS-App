from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError


class DepartmentAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(
        "students.Department",
        on_delete=models.CASCADE,
        related_name="department_admins",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Ensure user is not already an admin for another department
        if DepartmentAdmin.objects.exclude(pk=self.pk).filter(user=self.user).exists():
            raise ValidationError(
                "This user is already an admin for another department"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.department.name} Admin"

    class Meta:
        verbose_name = "Department Admin"
        verbose_name_plural = "Department Admins"
        unique_together = ["user", "department"]


class CustomUser(User):
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    class Meta:
        proxy = True

    @property
    def is_department_admin(self):
        return hasattr(self, "departmentadmin")

    @property
    def department(self):
        if self.is_department_admin:
            return self.departmentadmin.department
        return None

    @property
    def role(self):
        if self.is_superuser:
            return "Superuser"
        elif self.is_department_admin:
            return f"{self.department.name} Admin"
        return "User"
