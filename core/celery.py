import os 
from celery import Celery

os.environ.setdefault("DJANGO_SETTING_MODULE","core.settings")
app = Celery('singshop')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks