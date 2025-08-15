from celery import shared_task
from .models import Transfer
from django.utils import timezone

@shared_task
def process_pending_transfers():
    """
    Периодически проверяет все переводы в статусе 'pending' и переводит их в 'completed'
    """
    pending_transfers = Transfer.objects.filter(status="pending")
    for transfer in pending_transfers:
        transfer.status = "completed"
        transfer.completed_at = timezone.now()
        transfer.save()
    return f"Processed {pending_transfers.count()} transfers."
