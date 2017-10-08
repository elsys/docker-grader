from django.core.management import call_command
from django.utils.six import StringIO

import pytest


@pytest.fixture
def task(monkeypatch):
    class Task:
        @classmethod
        def from_dir(cls, *args, **kwargs):
            t.from_dir_args = args
            t.from_dir_kwargs = kwargs
            return t

        def grade(self, *args, **kwargs):
            self.grade_args = args
            self.grade_kwargs = kwargs

            return t.step_results

    t = Task()
    t.max_marks = 0
    t.step_results = tuple()

    monkeypatch.setattr('tasks.management.commands.testtask.Task', Task)
    return t


def test_tasktask_command_no_steps(task):
    task.max_marks = 400

    out = StringIO()
    err = StringIO()
    call_command('testtask', 'definition/path', '/tmp/test.c',
                 stdout=out, stderr=err)

    assert task.from_dir_args == ('definition/path',)
    assert len(task.from_dir_kwargs) == 0

    assert task.grade_args == ('/tmp/test.c',)
    assert len(task.grade_kwargs) == 0

    assert out.getvalue() == ''
    assert 'Total marks: 0/400' in err.getvalue()


def test_tasktask_command_success_step(task):
    task.max_marks = 200
    task.step_results = [('ts1', {
        'marks': 200,
        'fail': False,
        'max_marks': 200,
        'output_msg': 'TS1 Succeeded',
    })]

    out = StringIO()
    err = StringIO()
    call_command('testtask', 'definition/path', '/tmp/test.c',
                 stdout=out, stderr=err)

    assert task.from_dir_args == ('definition/path',)
    assert len(task.from_dir_kwargs) == 0

    assert task.grade_args == ('/tmp/test.c',)
    assert len(task.grade_kwargs) == 0

    assert out.getvalue() == ''

    assert 'Step: ts1\n' in err.getvalue()
    assert 'Marks: 200/200\n' in err.getvalue()
    assert 'TS1 Succeeded\n' in err.getvalue()
    assert 'stdplex:\n\n' in err.getvalue()

    assert 'Total marks: 200/200\n' in err.getvalue()


def test_tasktask_command_partial_step(task):
    task.max_marks = 200
    task.step_results = [('ts1', {
        'marks': 100,
        'fail': False,
        'max_marks': 200,
        'output_msg': 'TS1 Partially succeeded',
    })]

    out = StringIO()
    err = StringIO()
    call_command('testtask', 'definition/path', '/tmp/test.c',
                 stdout=out, stderr=err)

    assert task.from_dir_args == ('definition/path',)
    assert len(task.from_dir_kwargs) == 0

    assert task.grade_args == ('/tmp/test.c',)
    assert len(task.grade_kwargs) == 0

    assert out.getvalue() == ''

    assert 'Step: ts1\n' in err.getvalue()
    assert 'Marks: 100/200\n' in err.getvalue()
    assert 'TS1 Partially succeeded\n' in err.getvalue()
    assert 'stdplex:\n\n' in err.getvalue()

    assert 'Total marks: 100/200\n' in err.getvalue()


def test_tasktask_command_fail_step(task):
    task.max_marks = 200
    task.step_results = [('ts1', {
        'marks': 0,
        'fail': True,
        'max_marks': 200,
        'output_msg': 'TS1 Failed',
        'testing_result': {
            'stdplex': 'Failed output',
        },
    })]

    out = StringIO()
    err = StringIO()
    call_command('testtask', 'definition/path', '/tmp/test.c',
                 stdout=out, stderr=err)

    assert task.from_dir_args == ('definition/path',)
    assert len(task.from_dir_kwargs) == 0

    assert task.grade_args == ('/tmp/test.c',)
    assert len(task.grade_kwargs) == 0

    assert out.getvalue() == ''

    assert 'Step: ts1\n' in err.getvalue()
    assert 'Marks: 0/200\n' in err.getvalue()
    assert 'TS1 Failed\n' in err.getvalue()
    assert 'stdplex:\nFailed output\n' in err.getvalue()

    assert 'Total marks: 0/200\n' in err.getvalue()
