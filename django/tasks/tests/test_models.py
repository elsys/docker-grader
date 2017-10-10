import pytest

from django.utils import timezone
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from tasks.models import Task
from tasks.models import TaskStep
from tasks.models import TaskSubmission
from tasks.models import TaskLog


@pytest.mark.django_db
def test_task():
    task = Task.objects.create(
        slug='test', description='Some text',
        grading_image='grading_image', testing_image='testing_image')

    db_task = Task.objects.get()
    assert task == db_task
    assert db_task.slug == 'test'
    assert db_task.description == 'Some text'
    assert db_task.grading_image == 'grading_image'
    assert db_task.testing_image == 'testing_image'
    assert db_task.max_marks == 0
    assert str(db_task) == 'test'


@pytest.mark.django_db
def test_task_default_description():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    db_task = Task.objects.get()
    assert task == db_task
    assert db_task.description == ''


@pytest.mark.django_db
def test_task_duplicate_slug():
    Task.objects.create(
        slug='test', description='Some text',
        grading_image='grading_image', testing_image='testing_image')

    with pytest.raises(IntegrityError) as excinfo:
        Task.objects.create(
            slug='test', description='Some text',
            grading_image='grading_image', testing_image='testing_image')

    assert '.slug' in str(excinfo.value)


@pytest.mark.django_db
def test_task_step():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    task_step = TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    db_task_step = TaskStep.objects.get()
    assert task_step == db_task_step
    assert db_task_step.task == task
    assert db_task_step.slug == 'ts1'
    assert db_task_step.order == 1
    assert db_task_step.max_marks == 20
    assert task.steps.count() == 1
    assert task.steps.get() == db_task_step
    assert task.max_marks == 20
    assert str(db_task_step) == str(task) + ' (001): ts1'


@pytest.mark.django_db
def test_task_step_duplicate_slug():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    with pytest.raises(IntegrityError) as excinfo:
        TaskStep.objects.create(
            task=task, slug='ts1', order=2, max_marks=40)

    assert '.slug' in str(excinfo.value)
    assert '.task_id' in str(excinfo.value)


@pytest.mark.django_db
def test_task_submission():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    db_task_submission = TaskSubmission.objects.get()
    assert task_submission == db_task_submission
    assert db_task_submission.task == task
    assert db_task_submission.user == user
    assert db_task_submission.max_marks == 20
    assert db_task_submission.total_marks == 10
    assert db_task_submission.broken is False

    assert task.submissions.count() == 1
    assert task.submissions.get() == db_task_submission

    assert user.submissions.count() == 1
    assert user.submissions.get() == db_task_submission

    assert str(db_task_submission) == str(task) + ': user (10/20; 50%)'


@pytest.mark.django_db
def test_task_submission_no_steps():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=0, total_marks=0,
        broken=False)

    db_task_submission = TaskSubmission.objects.get()
    assert task_submission == db_task_submission
    assert str(db_task_submission) == str(task) + ': user (0/0; 100%)'


@pytest.mark.django_db
def test_task_submission_default_total_marks():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, broken=False)

    db_task_submission = TaskSubmission.objects.get()
    assert task_submission == db_task_submission
    assert db_task_submission.total_marks == 0


@pytest.mark.django_db
def test_task_submission_default_broken():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=0)

    db_task_submission = TaskSubmission.objects.get()
    assert task_submission == db_task_submission
    assert db_task_submission.broken is True


@pytest.mark.django_db
def test_task_log_submitted():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission, action=TaskLog.LOG_TYPE.SUBMITTED,
        message='Task submitted!')

    now = timezone.now()

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_submission == task_submission
    assert db_task_log.task_step is None
    assert (now - task_log.date).total_seconds() < 60
    assert db_task_log.action == TaskLog.LOG_TYPE.SUBMITTED
    assert db_task_log.marks is None
    assert db_task_log.max_marks is None
    assert db_task_log.message == 'Task submitted!'

    assert task_submission.log.count() == 1
    assert task_submission.log.get() == db_task_log

    assert str(db_task_log) == str(task_submission) + ': Submitted'


@pytest.mark.django_db
def test_task_log_grading_started():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission,
        action=TaskLog.LOG_TYPE.GRADING_STARTED,
        message='Task grading started!')

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_step is None
    assert db_task_log.action == TaskLog.LOG_TYPE.GRADING_STARTED
    assert db_task_log.marks is None
    assert db_task_log.max_marks is None
    assert db_task_log.message == 'Task grading started!'

    assert str(db_task_log) == str(task_submission) + ': Grading started'


@pytest.mark.django_db
def test_task_log_regrading_started():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission,
        action=TaskLog.LOG_TYPE.REGRADING_STARTED,
        message='Task regrading started!')

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_step is None
    assert db_task_log.action == TaskLog.LOG_TYPE.REGRADING_STARTED
    assert db_task_log.marks is None
    assert db_task_log.max_marks is None
    assert db_task_log.message == 'Task regrading started!'

    assert str(db_task_log) == str(task_submission) + ': Regrading started'


@pytest.mark.django_db
def test_task_log_succeeded():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    task_step = TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission,
        task_step=task_step,
        action=TaskLog.LOG_TYPE.SUCCEEDED,
        marks=20,
        max_marks=20,
        message='Task step succeeded!')

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_step == task_step
    assert db_task_log.action == TaskLog.LOG_TYPE.SUCCEEDED
    assert db_task_log.marks == 20
    assert db_task_log.max_marks == 20
    assert db_task_log.message == 'Task step succeeded!'

    assert task_step.log.count() == 1
    assert task_step.log.get() == db_task_log

    assert str(db_task_log) == str(task_submission) + ': Succeeded'


@pytest.mark.django_db
def test_task_log_partially_succeeded():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    task_step = TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission,
        task_step=task_step,
        action=TaskLog.LOG_TYPE.PARTIALLY_SUCCEEDED,
        marks=10,
        max_marks=20,
        message='Task step partially succeeded!')

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_step == task_step
    assert db_task_log.action == TaskLog.LOG_TYPE.PARTIALLY_SUCCEEDED
    assert db_task_log.marks == 10
    assert db_task_log.max_marks == 20
    assert db_task_log.message == 'Task step partially succeeded!'

    assert task_step.log.count() == 1
    assert task_step.log.get() == db_task_log

    assert str(db_task_log) == str(task_submission) + ': Partially succeeded'


@pytest.mark.django_db
def test_task_log_failed():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    task_step = TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission,
        task_step=task_step,
        action=TaskLog.LOG_TYPE.FAILED,
        marks=0,
        max_marks=20,
        message='Task step failed!')

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_step == task_step
    assert db_task_log.action == TaskLog.LOG_TYPE.FAILED
    assert db_task_log.marks == 0
    assert db_task_log.max_marks == 20
    assert db_task_log.message == 'Task step failed!'

    assert task_step.log.count() == 1
    assert task_step.log.get() == db_task_log

    assert str(db_task_log) == str(task_submission) + ': Failed'


@pytest.mark.django_db
def test_task_log_broke():
    task = Task.objects.create(
        slug='test',
        grading_image='grading_image', testing_image='testing_image')

    task_step = TaskStep.objects.create(
        task=task, slug='ts1', order=1, max_marks=20)

    user = User.objects.create_user(username='user', email='user@localhost')

    task_submission = TaskSubmission.objects.create(
        task=task, user=user, max_marks=20, total_marks=10,
        broken=False)

    task_log = TaskLog.objects.create(
        task_submission=task_submission,
        task_step=task_step,
        action=TaskLog.LOG_TYPE.BROKE,
        marks=0,
        max_marks=20,
        message='Task step broke!')

    db_task_log = TaskLog.objects.get()
    assert task_log == db_task_log
    assert db_task_log.task_step == task_step
    assert db_task_log.action == TaskLog.LOG_TYPE.BROKE
    assert db_task_log.marks == 0
    assert db_task_log.max_marks == 20
    assert db_task_log.message == 'Task step broke!'

    assert task_step.log.count() == 1
    assert task_step.log.get() == db_task_log

    assert str(db_task_log) == str(task_submission) + ': Broke'
