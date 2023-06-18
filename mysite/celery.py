import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'retrieve_messages_from_cache_and_save_to_db': {
        'task': 'chat.tasks.messages_to_db',
        'schedule': crontab(minute='*/5')
    },
}
