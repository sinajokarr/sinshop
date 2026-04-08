from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Cart

@shared_task
def clear_abandoned_carts():
    threshold = timezone.now() - timedelta(days=2)
    abandoned_carts = Cart.objects.filter(updated_at__lt=threshold, user__isnull=True)
    count = abandoned_carts.count()
    abandoned_carts.delete()
    return f"Deleted {count} abandoned carts."