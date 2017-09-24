from urllib.parse import urlparse

from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from tasks.models import Task
from tasks.models import TaskSubmission


@pytest.mark.django_db
def test_empty_file_upload(admin_client):
    task = Task.objects.create(slug='test')

    url = reverse('task', kwargs={'task_id': task.id})

    zip_file = SimpleUploadedFile(
        "task1.zip", "", content_type="application/zip")

    response = admin_client.post(url, {'zip_file': zip_file})
    assert response.status_code == 400


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_valid_file_upload(admin_client):
    task = Task.objects.create(slug='test')
    data = b"a"

    url = reverse('task', kwargs={'task_id': task.id})

    zip_file = SimpleUploadedFile(
        "task1.zip", data, content_type="application/zip")

    response = admin_client.post(url, {'zip_file': zip_file})
    assert response.status_code == 302
    assert urlparse(response.url).path == url

    submissions = TaskSubmission.objects.all()
    assert len(submissions) == 1

    submission = submissions[0]

    with open(submission.get_submission_path(), 'rb') as f:
        assert data == f.read()
