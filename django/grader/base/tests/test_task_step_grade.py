import pytest

from grader.base.task import TaskStep


@pytest.fixture
def grading_runner():
    class Runner:
        def __init__(self):
            self.preprocess_raise = False
            self.preprocess_mix_result = {}

            self.postprocess_raise = False
            self.postprocess_mix_result = {}

        def rpc_call(self, fn, step_name, kwargs):
            result = {}

            if fn == 'run_preprocess':
                if self.preprocess_raise is True:
                    raise
                mix_result = self.preprocess_mix_result
            else:
                if self.postprocess_raise is True:
                    raise
                mix_result = self.postprocess_mix_result

            state = {
                'fn': fn,
                'step_name': step_name,
                'kwargs': kwargs,
            }

            result = {
                'stop_on_failure': True,
                'command': 'sleep',
                'state': state,
            }
            result.update(mix_result)
            return result

    return Runner()


@pytest.fixture
def testing_runner():
    class Runner:
        def __init__(self):
            self.test_raise = False
            self.test_mix_stdout = None
            self.test_mix_stderr = None
            self.test_mix_stdplex = None

        def exec_step(self, command):
            if self.test_raise:
                raise

            if isinstance(command, list):
                command = ' '.join(command)

            rc = 0

            if self.test_mix_stdout is None:
                stdout = command.encode('ascii')
            else:
                stdout = self.test_mix_stdout

            if self.test_mix_stderr is None:
                stderr = b''
            else:
                stderr = self.test_mix_stderr

            if self.test_mix_stdplex is None:
                stdplex = b''
            else:
                stdplex = self.test_mix_stdplex

            return rc, stdout, stderr, stdplex

    return Runner()


def test_task_step_run_preprocess(grading_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    result = task_step.run_preprocess(grading_runner, kwargs)
    result_state = result['state']

    assert result_state == state
    assert 'c' not in state

    assert result_state['fn'] == 'run_preprocess'
    assert result_state['step_name'] == 'ts1'
    assert result_state['kwargs'] == kwargs


def test_task_step_run_test_str(testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    command = 'sleep infinity'
    kwargs = {'command': command}

    result = task_step.run_test(testing_runner, kwargs)
    expected_command = b'/bin/bash -c \'sleep infinity\''

    assert result['rc'] == 0
    assert result['stdout'] == expected_command
    assert result['stderr'] == b''
    assert result['stdplex'] == b''


def test_task_step_run_test_str_escape(testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    command = 'sleep \'infinity\''
    kwargs = {'command': command}

    result = task_step.run_test(testing_runner, kwargs)
    expected_command = b'/bin/bash -c \'sleep \'"\'"\'infinity\'"\'"\'\''

    assert result['rc'] == 0
    assert result['stdout'] == expected_command
    assert result['stderr'] == b''
    assert result['stdplex'] == b''


def test_task_step_run_test_array(testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    command = ['sleep', 'infinity']
    kwargs = {'command': command}

    result = task_step.run_test(testing_runner, kwargs)
    expected_command = b'sleep infinity'

    assert result['rc'] == 0
    assert result['stdout'] == expected_command
    assert result['stderr'] == b''
    assert result['stdplex'] == b''


def test_task_step_run_postprocess(grading_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    result = task_step.run_postprocess(grading_runner, kwargs)
    result_state = result['state']

    assert result_state == state
    assert 'c' not in state

    assert result_state['fn'] == 'run_postprocess'
    assert result_state['step_name'] == 'ts1'
    assert result_state['kwargs'] == kwargs


def test_task_step_grade_preprocess_raise(grading_runner, testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_test_raise_default(grading_runner, testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    testing_runner.test_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_test_raise_continue(grading_runner, testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    testing_runner.test_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is True
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_test_raise_not_continue(grading_runner,
                                                 testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    testing_runner.test_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_test_stdout_non_ascii_default(grading_runner,
                                                       testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    testing_runner.test_mix_stdout = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stdout_continue(grading_runner,
                                              testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    testing_runner.test_mix_stdout = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is True
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stdout_not_continue(grading_runner,
                                                  testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    testing_runner.test_mix_stdout = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stderr_non_ascii_default(grading_runner,
                                                       testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    testing_runner.test_mix_stderr = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stderr_continue(grading_runner,
                                              testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    testing_runner.test_mix_stderr = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is True
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stderr_not_continue(grading_runner,
                                                  testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    testing_runner.test_mix_stderr = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stdplex_non_ascii_default(grading_runner,
                                                        testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    testing_runner.test_mix_stdplex = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stdplex_continue(grading_runner,
                                               testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    testing_runner.test_mix_stdplex = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is True
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_test_stdplex_not_continue(grading_runner,
                                                   testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    testing_runner.test_mix_stdplex = b'\x80'
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'non-ascii' in result['output_msg']


def test_task_step_grade_postprocess_raise_default(grading_runner,
                                                   testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.postprocess_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_postprocess_raise_continue(grading_runner,
                                                    testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    grading_runner.postprocess_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is True
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_postprocess_raise_not_continue(grading_runner,
                                                        testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    grading_runner.postprocess_raise = True
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is True
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'contact your teacher' in result['output_msg']


def test_task_step_grade_postprocess_fail_default(grading_runner,
                                                  testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.postprocess_mix_result = {
        'fail': True,
        'output_msg': 'Failed'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'Failed' in result['output_msg']


def test_task_step_grade_postprocess_fail_continue(grading_runner,
                                                   testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    grading_runner.postprocess_mix_result = {
        'fail': True,
        'output_msg': 'Failed'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is True
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'Failed' in result['output_msg']


def test_task_step_grade_postprocess_fail_not_continue(grading_runner,
                                                       testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 100})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    grading_runner.postprocess_mix_result = {
        'fail': True,
        'output_msg': 'Failed'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is True
    assert result['continue'] is False
    assert result['marks'] == 0
    assert result['max_marks'] == 100
    assert 'Failed' in result['output_msg']


def test_task_step_grade_postprocess_success_default(grading_runner,
                                                     testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 50})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.postprocess_mix_result = {
        'grade': 100,
        'fail': False,
        'output_msg': 'Success'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is False
    assert result['continue'] is True
    assert result['marks'] == 50
    assert result['max_marks'] == 50
    assert 'Success' in result['output_msg']


def test_task_step_grade_postprocess_success_continue(grading_runner,
                                                      testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 50})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    grading_runner.postprocess_mix_result = {
        'grade': 100,
        'fail': False,
        'output_msg': 'Success'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is False
    assert result['continue'] is True
    assert result['marks'] == 50
    assert result['max_marks'] == 50
    assert 'Success' in result['output_msg']


def test_task_step_grade_postprocess_success_not_continue(grading_runner,
                                                          testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 50})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    grading_runner.postprocess_mix_result = {
        'grade': 100,
        'fail': False,
        'output_msg': 'Success'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is False
    assert result['continue'] is True
    assert result['marks'] == 50
    assert result['max_marks'] == 50
    assert 'Success' in result['output_msg']


def test_task_step_grade_postprocess_partial_success_default(grading_runner,
                                                             testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 50})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.postprocess_mix_result = {
        'grade': 25,
        'fail': False,
        'output_msg': 'Partial success'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is False
    assert result['continue'] is True
    assert result['marks'] == 12
    assert result['max_marks'] == 50
    assert 'Partial' in result['output_msg']


def test_task_step_grade_postprocess_partial_success_continue(grading_runner,
                                                              testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 50})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': False}
    grading_runner.postprocess_mix_result = {
        'grade': 25,
        'fail': False,
        'output_msg': 'Partial success'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is False
    assert result['continue'] is True
    assert result['marks'] == 12
    assert result['max_marks'] == 50
    assert 'Partial' in result['output_msg']


def test_task_step_grade_postprocess_partial_success_not_continue(
        grading_runner, testing_runner):
    task_step = TaskStep('ts1', {'max_marks': 50})

    state = {'c': -1}
    kwargs = {'a': 1, 'b': 100, 'state': state}

    grading_runner.preprocess_mix_result = {'stop_on_failure': True}
    grading_runner.postprocess_mix_result = {
        'grade': 25,
        'fail': False,
        'output_msg': 'Partial'
    }
    result = task_step.grade(grading_runner, testing_runner, kwargs)

    assert result['broken'] is False
    assert result['fail'] is False
    assert result['continue'] is True
    assert result['marks'] == 12
    assert result['max_marks'] == 50
    assert 'Partial' in result['output_msg']
