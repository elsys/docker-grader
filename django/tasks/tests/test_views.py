from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from tasks.models import Task
from tasks.forms import TaskForm


@pytest.fixture
def user(django_user_model, django_username_field):
    UserModel = django_user_model
    username_field = django_username_field

    try:
        user = UserModel._default_manager.get(**{username_field: 'user'})
    except UserModel.DoesNotExist:
        extra_fields = {}
        user = UserModel._default_manager.create_user(
            'user', 'user@localhost', 'password', **extra_fields)

    return user


@pytest.fixture
def user_client(client, user):
    from django.test.client import Client

    client = Client()
    client.login(username=user.username, password='password')

    return client


@pytest.fixture
def task(db):
    task = Task.objects.create(
        slug='test', description='Some text',
        grading_image='grading_image', testing_image='testing_image')

    return task


def test_not_logged_user(client, task):
    response = client.get(reverse('task', kwargs={'task_id': task.id}))
    assert response.status_code == 302
    assert 'login' in response['Location']


def test_not_existant_task(user_client):
    response = user_client.get(reverse('task', kwargs={'task_id': 42}))
    assert response.status_code == 404


def test_display_task(user_client, task):
    response = user_client.get(reverse('task', kwargs={'task_id': task.id}))
    assert response.status_code == 200

    assert isinstance(response.context['form'], TaskForm)
    assert response.context['data_url'] == reverse(
        'task-submissions', kwargs={'task_id': task.id})
    assert response.context['task'].id == task.id

    assert task.slug in response.content.decode()
    assert task.description in response.content.decode()


def test_submit_invalid(user_client, task):
    response = user_client.post(
        reverse('task', kwargs={'task_id': task.id}), {})
    assert response.status_code == 400

    assert isinstance(response.context['form'], TaskForm)
    assert response.context['data_url'] == reverse(
        'task-submissions', kwargs={'task_id': task.id})
    assert response.context['task'].id == task.id

    assert task.slug in response.content.decode()
    assert task.description in response.content.decode()


def test_submit_valid(monkeypatch, user_client, user, task):
    def submit_submission(*args, **kwargs):
        contents = args[2]
        submit_submission.last_read = contents.read()

        submit_submission.last_args = args
        submit_submission.last_kwargs = kwargs

    monkeypatch.setattr(
        'tasks.views.TaskSubmission.objects.submit_submission',
        submit_submission)

    content = SimpleUploadedFile('test.c', b'#include')

    task_url = reverse('task', kwargs={'task_id': task.id})
    response = user_client.post(task_url, {'submission': content})
    assert response.status_code == 302
    assert response['Location'] == task_url

    assert len(submit_submission.last_kwargs) == 0

    (submitted_task, submitted_user, submitted_contents) = \
        submit_submission.last_args

    assert submitted_task.id == task.id
    assert submitted_user.id == user.id
    assert submit_submission.last_read == b'#include'
