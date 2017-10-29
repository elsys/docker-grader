import os
import uuid
import shutil

from django.db import models
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.models import User


class Task(models.Model):
    slug = models.SlugField(max_length=255, unique=True)

    grading_image = models.CharField(max_length=1023)
    testing_image = models.CharField(max_length=1023)

    description = models.TextField(default='')

    def get_task_dir(self):
        return os.path.join(settings.GRADER_SUBMISSIONS_DIR, self.slug)

    @classmethod
    def from_mem_task(cls, mem_task, slug):
        with transaction.atomic():
            task = Task.objects.create(
                slug=slug,
                grading_image=mem_task.grading_image,
                testing_image=mem_task.testing_image)

            order = 1
            for step_name, mem_task_step in mem_task.steps.items():
                TaskStep.objects.create(
                    task=task,
                    slug=mem_task_step.name,
                    order=order,
                    max_marks=mem_task_step.max_marks)
                order += 1

        return task

    def __str__(self):
        return self.slug

    @property
    def max_marks(self):
        sum_marks = self.steps.aggregate(
            models.Sum('max_marks'))['max_marks__sum']
        if sum_marks is None:
            return 0
        return sum_marks


class TaskStep(models.Model):
    task = models.ForeignKey(Task, related_name='steps')
    slug = models.SlugField(max_length=255)
    order = models.SmallIntegerField()

    max_marks = models.IntegerField()

    def __str__(self):
        return '{0!s} ({1:03d}): {2!s}'.format(
            self.task, self.order, self.slug)

    class Meta:
        unique_together = ('task', 'slug',)


class TaskSubmissionManager(models.Manager):
    def submit_submission(self, task, user, contents):
        task_dir = task.get_task_dir()
        os.makedirs(task_dir, mode=0o2777, exist_ok=True)

        submission = self.model.objects.create(task=task, user=user)
        file_path = submission.get_submission_path()

        with open(file_path, 'wb+') as destination:
            shutil.copyfileobj(contents, destination)

        TaskLog.objects.create(
            task_submission=submission, action=TaskLog.LOG_TYPE.SUBMITTED)

        submission.grade()

        return submission


class TaskSubmission(models.Model):
    objects = TaskSubmissionManager()

    task = models.ForeignKey(Task, related_name='submissions')
    user = models.ForeignKey(User, related_name='submissions')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    max_marks = models.IntegerField()
    total_marks = models.IntegerField(default=0)
    broken = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.max_marks = self.task.max_marks
        return super().save(*args, **kwargs)

    def get_submission_path(self):
        return os.path.join(self.task.get_task_dir(), str(self.uuid))

    def grade(self, regrade=False):
        from tasks import tasks
        tasks.grade.delay(self.id)

    def __str__(self):
        task_max_marks = self.task.max_marks
        if task_max_marks == 0:
            percent = 100
        else:
            percent = self.total_marks * 100 // task_max_marks

        return '{0!s}: {1!s} ({2:d}/{3:d}; {4:d}%)'.format(
            self.task, self.user.get_username(),
            self.total_marks, task_max_marks, percent)


class TaskLog(models.Model):
    class LOG_TYPE:
        SUBMITTED = 'SUBMITTED'
        GRADING_STARTED = 'GRADING_STARTED'
        REGRADING_STARTED = 'REGRADING_STARTED'
        SUCCEEDED = 'SUCCEEDED'
        PARTIALLY_SUCCEEDED = 'PARTIALLY_SUCCEEDED'
        FAILED = 'FAILED'
        BROKE = 'BROKE'

    DJANGO_LOG_TYPES = (
        (LOG_TYPE.SUBMITTED, 'Submitted'),
        (LOG_TYPE.GRADING_STARTED, 'Grading started'),
        (LOG_TYPE.REGRADING_STARTED, 'Regrading started'),
        (LOG_TYPE.SUCCEEDED, 'Succeeded'),
        (LOG_TYPE.PARTIALLY_SUCCEEDED, 'Partially succeeded'),
        (LOG_TYPE.FAILED, 'Failed'),
        (LOG_TYPE.BROKE, 'Broke'),
    )
    LOG_TYPES = tuple(c[0] for c in DJANGO_LOG_TYPES)

    task_submission = models.ForeignKey(TaskSubmission, related_name='log')
    task_step = models.ForeignKey(TaskStep, related_name='log', null=True)
    date = models.DateTimeField(default=timezone.now, editable=False)
    action = models.CharField(max_length=31, choices=DJANGO_LOG_TYPES)

    marks = models.IntegerField(null=True)
    max_marks = models.IntegerField(null=True)

    message = models.TextField()

    def __str__(self):
        return '{0!s}: {1!s}'.format(
            self.task_submission, self.get_action_display())
