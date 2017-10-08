from collections import OrderedDict

import pytest

from grader.base.task import TaskStep
from grader.base.task import Task


@pytest.fixture
def grading_runner():
    class Runner:
        def __init__(self, docker_image):
            Runner.last_instance = self

            self.docker_image = docker_image

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    return Runner


@pytest.fixture
def testing_runner():
    class Runner:
        def __init__(self, docker_image, input_path):
            Runner.last_instance = self

            self.docker_image = docker_image
            self.input_path = input_path
            self.input_file_container_path = 'container/path/file.c'

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    return Runner


def test_task_grade_basic(monkeypatch, grading_runner, testing_runner):
    task = Task('grading_image_basic', 'testing_image_basic', {})
    test_file_path = 'host/path/file.c'

    monkeypatch.setattr('grader.base.task.GradingRunner', grading_runner)
    monkeypatch.setattr('grader.base.task.TestingRunner', testing_runner)

    assert sum(1 for s in task.grade(test_file_path)) == 0

    assert grading_runner.last_instance.docker_image == 'grading_image_basic'

    assert testing_runner.last_instance.docker_image == 'testing_image_basic'
    assert testing_runner.last_instance.input_path == test_file_path


def test_task_grade_single_task(monkeypatch, grading_runner, testing_runner):
    def grade(self, grading_runner_instance, testing_runner_instance, kwargs):
        assert isinstance(grading_runner_instance, grading_runner)
        assert isinstance(testing_runner_instance, testing_runner)
        assert 'state' in kwargs
        assert kwargs['filename'] == \
            testing_runner_instance.input_file_container_path

        return self.step_result

    task_step1 = TaskStep('ts1', {'max_marks': 25})
    task_step1.step_result = {'result': 42, 'continue': True}

    task_steps = OrderedDict([('ts1', task_step1)])
    task = Task('grading_image_basic', 'testing_image_basic', task_steps)
    test_file_path = 'host/path/file.c'

    monkeypatch.setattr('grader.base.task.GradingRunner', grading_runner)
    monkeypatch.setattr('grader.base.task.TestingRunner', testing_runner)
    monkeypatch.setattr('grader.base.task.TaskStep.grade', grade)

    steps_count = 0
    for step_name, step_result in task.grade(test_file_path):
        steps_count += 1
        assert step_name == task_step1.name
        assert step_result == task_step1.step_result

    assert steps_count == 1


def test_task_grade_multiple_steps(
        monkeypatch, grading_runner, testing_runner):
    def grade(self, *args, **kwargs):
        return self.step_result

    task_step1 = TaskStep('ts1', {'max_marks': 25})
    task_step1.step_result = {'result': 42, 'continue': True}

    task_step2 = TaskStep('ts2', {'max_marks': 50})
    task_step2.step_result = {'result': 43, 'continue': True}

    task_steps = OrderedDict([('ts1', task_step1), ('ts2', task_step2)])
    task = Task('grading_image_basic', 'testing_image_basic', task_steps)
    test_file_path = 'host/path/file.c'

    monkeypatch.setattr('grader.base.task.GradingRunner', grading_runner)
    monkeypatch.setattr('grader.base.task.TestingRunner', testing_runner)
    monkeypatch.setattr('grader.base.task.TaskStep.grade', grade)

    steps_count = 0
    expected_step = task_step1
    for step_name, step_result in task.grade(test_file_path):
        steps_count += 1
        assert step_name == expected_step.name
        assert step_result == expected_step.step_result

        expected_step = task_step2

    assert steps_count == 2


def test_task_grade_multiple_steps_break(
        monkeypatch, grading_runner, testing_runner):
    def grade(self, *args, **kwargs):
        return self.step_result

    task_step1 = TaskStep('ts1', {'max_marks': 25})
    task_step1.step_result = {'result': 42, 'continue': False}

    task_step2 = TaskStep('ts2', {'max_marks': 50})
    task_step2.step_result = {'result': 43, 'continue': True}

    task_steps = OrderedDict([('ts1', task_step1), ('ts2', task_step2)])
    task = Task('grading_image_basic', 'testing_image_basic', task_steps)
    test_file_path = 'host/path/file.c'

    monkeypatch.setattr('grader.base.task.GradingRunner', grading_runner)
    monkeypatch.setattr('grader.base.task.TestingRunner', testing_runner)
    monkeypatch.setattr('grader.base.task.TaskStep.grade', grade)

    steps_count = 0
    for step_name, step_result in task.grade(test_file_path):
        steps_count += 1
        assert step_name == task_step1.name
        assert step_result == task_step1.step_result

    assert steps_count == 1
