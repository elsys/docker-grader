from collections import OrderedDict

from grader.base.task import Task
from grader.base.task import TaskStep


def test_task_empty_init():
    task = Task('grading_image', 'testing_image', {})
    assert task.grading_image == 'grading_image'
    assert task.testing_image == 'testing_image'
    assert len(task.steps) == 0
    assert task.max_marks == 0


def test_task_step_init():
    task_step = TaskStep('ts1', {'max_marks': 100})
    assert task_step.name == 'ts1'
    assert task_step.max_marks == 100


def test_task_init_1():
    task_step1 = TaskStep('ts1', {'max_marks': 0})
    task_step2 = TaskStep('ts2', {'max_marks': 50})
    task_steps = OrderedDict(
        [('ts1', task_step1), ('ts2', task_step2)])

    task = Task('gi', 'ti', task_steps)
    assert task.grading_image == 'gi'
    assert task.testing_image == 'ti'
    assert len(task.steps) == 2
    assert task.max_marks == 50

    fs_name, first_step = task.steps.popitem(last=False)
    assert fs_name == 'ts1'
    assert first_step.name == 'ts1'
    assert first_step.max_marks == 0

    ss_name, second_step = task.steps.popitem(last=False)
    assert ss_name == 'ts2'
    assert second_step.name == 'ts2'
    assert second_step.max_marks == 50


def test_task_from_dir(tmpdir, monkeypatch):
    info_str = """
steps:
  compile:
    max_marks: 0
  forbidden_funcs:
    max_marks: 10
"""

    task_dir = tmpdir.mkdir('test_task')
    info_file = task_dir.join('info.yaml')
    info_file.write(info_str)
    sample_task_dir = task_dir.strpath

    def build(tag, *args, **kwargs):
        return tag

    monkeypatch.setattr('grader.base.task.docker_image_build', build)

    task = Task.from_dir(sample_task_dir)
    assert task.grading_image == 'test_task/grading'
    assert task.testing_image == 'test_task/testing'
    assert len(task.steps) == 2
    assert task.max_marks == 10

    s1_name, s1 = task.steps.popitem(last=False)
    assert s1_name == 'compile'
    assert s1.name == 'compile'
    assert s1.max_marks == 0

    s2_name, s2 = task.steps.popitem(last=False)
    assert s2_name == 'forbidden_funcs'
    assert s2.name == 'forbidden_funcs'
    assert s2.max_marks == 10
