from django.db import models
from django.utils import timezone

from authentication.models import User


class Task(models.Model):
    pass


class TaskStep(models.Model):
    task = models.ForeignKey(Task, related_name='steps')


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, related_name='submissions')
    user = models.ForeignKey(User, related_name='submissions')


class TaskLog(models.Model):
    class LOG_TYPE:
        SUBMIT = 'SUBMIT'
        CANCEL = 'CANCEL'

    DJANGO_LOG_TYPES = (
        (LOG_TYPE.SUBMIT, 'Submit'),
        (LOG_TYPE.CANCEL, 'Canel'),
    )
    LOG_TYPES = tuple(c[0] for c in DJANGO_LOG_TYPES)

    task_submission = models.ForeignKey(TaskSubmission, related_name='log')
    date = models.DateTimeField(default=timezone.now, editable=False)
    action = models.CharField(max_length=15, choices=DJANGO_LOG_TYPES)
    extra = models.TextField()
