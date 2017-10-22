from types import SimpleNamespace

from django.core.management import call_command
from django.utils.six import StringIO

import pytest


@pytest.fixture
def task(monkeypatch):
    class MemTask:
        @classmethod
        def from_dir(cls, *args, **kwargs):
            patch.from_dir_args = args
            patch.from_dir_kwargs = kwargs
            return patch

    class Task:
        @classmethod
        def from_mem_task(cls, *args, **kwargs):
            patch.from_mem_task_args = args
            patch.from_mem_task_kwargs = kwargs
            return patch

    patch = SimpleNamespace()

    monkeypatch.setattr(
        'tasks.management.commands.importtask.MemTask', MemTask)
    monkeypatch.setattr('tasks.management.commands.importtask.Task', Task)

    return patch


def test_importtask_command(task):
    out = StringIO()
    err = StringIO()
    call_command('importtask', 'cat', 'definition/path',
                 stdout=out, stderr=err)

    assert task.from_dir_args == ('definition/path',)
    assert len(task.from_dir_kwargs) == 0

    assert task.from_mem_task_args == (task, 'cat',)
    assert len(task.from_mem_task_kwargs) == 0

    assert err.getvalue() == ''
    assert 'Reading task definition from directory... Done.' in out.getvalue()
    assert 'Importing task definition to database... Done.' in out.getvalue()
