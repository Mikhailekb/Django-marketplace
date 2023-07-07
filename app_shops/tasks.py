from celery import shared_task
from django.utils import timezone
from django.utils.module_loading import import_string
from djmoney import settings

from .models.discount import Discount


@shared_task(name='discount_invalidate')
def discount_invalidate():
    """Аннулирование скидок, у которых истек строк действия"""
    current_time = timezone.now()
    discounts = Discount.objects.filter(date_end__lte=current_time, is_active=True)
    discounts.update(is_active=False)


@shared_task(name='update_rates')
def update_rates(backend=settings.EXCHANGE_BACKEND, **kwargs):
    """Обновление курса валют"""
    backend = import_string(backend)()
    backend.update_rates(**kwargs)
