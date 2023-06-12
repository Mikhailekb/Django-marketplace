import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_marketplace.settings')
app = Celery('django_marketplace')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'auto_discount_invalidate': {
        'task': 'discount_invalidate',
        'schedule': crontab(minute='00')
    }
}
app.autodiscover_tasks()
