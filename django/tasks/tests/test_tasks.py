from tasks.tasks import grade, TaskRunner
from django.test.utils import override_settings
import os


def test_docker():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    runner = TaskRunner("gcc:latest", dir_path + "/hello.c")
    runner.exec_step("gcc -x c /mnt/input")
    result = runner.exec_step("./a.out")
    assert result.decode("utf8") == "hello world\n"


@override_settings(CELERY_ALWAYS_EAGER=True)
def test_queue():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    result = grade.delay(dir_path + "/hello.c")
    assert result.get().decode("utf8") == "hello world\n"
