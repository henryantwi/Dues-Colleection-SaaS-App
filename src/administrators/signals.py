from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from .models import DepartmentAdmin


@receiver(post_save, sender=DepartmentAdmin)
def update_user_permissions(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            user = instance.user
            user.is_staff = True
            user.save(update_fields=['is_staff'])


@receiver(post_delete, sender=DepartmentAdmin)
def revoke_user_permissions(sender, instance, **kwargs):
    with transaction.atomic():
        user = instance.user
        user.is_staff = False
        user.save(update_fields=['is_staff'])
