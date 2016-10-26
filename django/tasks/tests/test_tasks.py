import os
import pytest
import time

from tasks import tasks
from django.test.utils import override_settings
from tasks.models import Task, TaskSubmission, TaskStep, TaskLog
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
        time.sleep(1)
        s = xmlrpc.client.ServerProxy('http://localhost:7799')
        result = s.parse_output(TEST_OUTPUT_PARSING_SOURCE, 2, "stdout", "stderr", 15)
        assert result["state"] == 60
        assert result["grade"] == 30
        assert result["output_msg"] == "blabla"
        assert result["exec_next_step"]


@pytest.fixture
def generate_task_submission(db):
    task = Task.objects.create(docker_image="gcc:latest", slug="test_task")
    user = User.objects.create()
    TaskStep.objects.create(task=task,
                            input_source="command = \"gcc -x c /mnt/input\"",
                            output_source="",
                            order=1)
    TaskStep.objects.create(task=task,
                            input_source="command = \"./a.out\"",
                            output_source="state = stdout; grade=150",
                            order=2)
    taskSubmission = TaskSubmission.objects.create(task=task, user=user)

    if not os.path.exists(task.get_task_dir()):
        os.mkdir(task.get_task_dir())
    copyfile(HELLO_C_PATH, taskSubmission.get_submission_path())
    yield taskSubmission.id
    os.remove(taskSubmission.get_submission_path())


def test_grade(generate_task_submission):
    result = tasks.grade(generate_task_submission)
    assert result == "hello world\n"
    submission = TaskSubmission.objects.get(pk=generate_task_submission)
    assert abs(submission.grade - 150) < 0.0001
    count = 0
    for log_entry in submission.log.all():
        assert log_entry.action == TaskLog.LOG_TYPE.STEP_COMPLETED
        assert log_entry.date
        count = count + 1
    assert count == 2


@override_settings(CELERY_ALWAYS_EAGER=True)
def test_grade_with_queue(generate_task_submission):
    result = tasks.grade.delay(generate_task_submission)
    assert result.get() == "hello world\n"
    submission = TaskSubmission.objects.get(pk=generate_task_submission)
    assert abs(submission.grade - 150) < 0.0001
    count = 0
    for log_entry in submission.log.all():
        assert log_entry.action == TaskLog.LOG_TYPE.STEP_COMPLETED
        assert log_entry.date
        count = count + 1
    assert count == 2
