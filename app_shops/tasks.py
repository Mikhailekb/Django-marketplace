from celery import shared_task

from app_shops.models.discount import Discount
from django.utils import timezone

@shared_task(name="discount_invalidate")
def discount_invalidate():
    current_time = timezone.now()
    discounts = Discount.objects.filter(date_end__lte=current_time, is_active=True)
    for discount in discounts:
        discount.is_active = False
        discount.save()
