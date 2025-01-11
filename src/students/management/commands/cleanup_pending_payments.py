from django.core.management.base import BaseCommand
from students.models import PendingMomoPayment

class Command(BaseCommand):
    help = 'Cleans up all pending payments'

    def handle(self, *args, **options):
        # Get all pending payments without time filter
        pending = PendingMomoPayment.objects.all()
        count = pending.count()
        pending.delete()
        self.stdout.write(f"Deleted {count} pending payments")
