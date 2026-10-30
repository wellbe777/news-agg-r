import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsagg.settings')

app = Celery('newsagg')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
#app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "refresh-user-recommendations": {
        "task": "news.tasks.compute_recommendations_for_all_users",
        "schedule": crontab(minute=0, hour="*/2"),  # every 2 hours (minute=0, hour="*/2")
        "args": (100,),  # limit per user
    },    
    #"ping-every-60s": {
    #    "task": "news.tasks.ping",
    #    "schedule": 60.0,  # every 60 seconds
    #},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')