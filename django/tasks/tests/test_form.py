from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from tasks.models import Task


@pytest.mark.django_db
def test_empty_file_upload(client):
    task = Task.objects.create()

    url = reverse('task', kwargs={'task_id': task.id})

    zip_file = SimpleUploadedFile(
        "task1.zip", "", content_type="application/zip")

    response = client.post(url, {'zip_file': zip_file})
    assert response.status_code == 400


@pytest.mark.django_db
def test_valid_file_upload(client):
    task = Task.objects.create()

    url = reverse('task', kwargs={'task_id': task.id})

    zip_file = SimpleUploadedFile(
        "task1.zip", b"a", content_type="application/zip")

    response = client.post(url, {'zip_file': zip_file})
    assert response.status_code == 302
