import os
import pytest
import time

from tasks import tasks
from django.test.utils import override_settings
from tasks.models import Task, TaskSubmission, TaskStep
from authentication.models import User
from shutil import copyfile
import xmlrpc.client


HELLO_C_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hello.c")


def test_docker_gcc():
    with tasks.TaskRunner("gcc:latest", HELLO_C_PATH) as runner:
        runner.exec_step("gcc -x c /mnt/input")
        result = runner.exec_step("./a.out")
        assert result.decode("utf8") == "hello world\n"


TEST_OUTPUT_PARSING_SOURCE = """
output_msg = "blabla"
grade = state * status_code
state = 2 * grade
exec_next_step = True
"""


def test_docker_python_rpc():
    with tasks.GradingStepsRunner():
        time.sleep(5)
        s = xmlrpc.client.ServerProxy('http://localhost:7799')
        result = s.parse_output(TEST_OUTPUT_PARSING_SOURCE, 2, "stdout", "stderr", 15)
        assert result["state"] == 60
        assert result["grade"] == 30
        assert result["output_msg"] == "blabla"
        assert result["exec_next_step"]


@pytest.mark.django_db
@override_settings(CELERY_ALWAYS_EAGER=True)
def test_queue():
    task = Task.objects.create(docker_image="gcc:latest", slug="test_task")
    user = User.objects.create()
    TaskStep.objects.create(task=task, input_source="gcc -x c /mnt/input", order=1)
    TaskStep.objects.create(task=task, input_source="./a.out", order=2)
    taskSubmission = TaskSubmission.objects.create(task=task, user=user)

    if not os.path.exists(task.get_task_dir()):
        os.mkdir(task.get_task_dir())
    copyfile(HELLO_C_PATH, taskSubmission.get_submission_path())

    result = tasks.grade.delay(taskSubmission.id)

    os.remove(taskSubmission.get_submission_path())
    assert result.get().decode("utf8") == "hello world\n"
