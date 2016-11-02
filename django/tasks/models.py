import os
import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.models import User


class Task(models.Model):
    slug = models.SlugField(max_length=31, unique=True)
    docker_image = models.CharField(max_length=255)
    description = models.TextField(null=True)

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
    grade = models.FloatField(default=0)
    grading_completed = models.BooleanField(default=False)

    def get_submission_path(self):
        return os.path.join(self.task.get_task_dir(), str(self.uuid))


class TaskLog(models.Model):
    class LOG_TYPE:
        SUBMITTED = 'SUBMITTED'
        CANCELED = 'CANCELED'
        STEP_COMPLETED = 'STEP_COMPLETED'
        STEP_FAILED = 'STEP_FAILED'

    DJANGO_LOG_TYPES = (
        (LOG_TYPE.SUBMITTED, 'Submitted'),
        (LOG_TYPE.CANCELED, 'Canceled'),
        (LOG_TYPE.STEP_COMPLETED, 'Step completed'),
        (LOG_TYPE.STEP_FAILED, 'Step failed'),
    )
    LOG_TYPES = tuple(c[0] for c in DJANGO_LOG_TYPES)

    task_submission = models.ForeignKey(TaskSubmission, related_name='log')
    date = models.DateTimeField(default=timezone.now, editable=False)
    action = models.CharField(max_length=15, choices=DJANGO_LOG_TYPES)
    extra = models.TextField()
