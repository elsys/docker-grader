from tasks.tasks import grade
from django.test.utils import override_settings


def test_docker():
    result = grade("aaa")
    assert result.decode("utf8") == "hello world\n"


@override_settings(CELERY_ALWAYS_EAGER=True)
def test_queue():
    result = grade.delay("aaa")
    assert result.get().decode("utf8") == "hello world\n"
