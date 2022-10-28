import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'Otp_projectAPI.settings')



app=Celery('Otp_projectAPI')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
from celery.schedules import crontab
app.conf.beat_schedule= { 
    'delete-expired-codes-every-1hour':{ 
        'task': 'Users.tasks.delete_invalid_codes',
        'schedule':3600
    }

}
app.conf.timezone='UTC'