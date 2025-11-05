from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')

app = Celery('auto_ski_info')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'monitor-x-accounts-every-15-minutes': {
        'task': 'x_monitor.tasks.monitor_all_active_accounts',
        'schedule': crontab(minute='*/15'),  # 15分ごとに実行
    },
}

app.conf.timezone = 'Asia/Tokyo'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')