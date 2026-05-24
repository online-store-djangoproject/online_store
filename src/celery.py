# src/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

app = Celery('online_store_kian')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
