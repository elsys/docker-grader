import os
import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings

from authentication.models import User


class Task(models.Model):
    slug = models.SlugField(max_length=31, unique=True)
    docker_image = models.CharField(max_length=255)

    def get_task_dir(self):
        return os.path.join(settings.GRADER_SUBMISSIONS_DIR, self.slug)


class TaskStep(models.Model):
    order = models.PositiveSmallIntegerField()
    task = models.ForeignKey(Task, related_name='steps')

    input_source = models.TextField()
    output_source = models.TextField()


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, related_name='submissions')
    user = models.ForeignKey(User, null=True, related_name='submissions')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)


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
