import os.path
import shlex
from collections import OrderedDict

from . import logger
from .utils import ordered_load
from .docker import docker_image_build
from .runners import GradingRunner, TestingRunner


class TaskStep:
    @classmethod
    def from_dir(cls, task_definition_dir, step_name, step_config):
        return cls(step_name, step_config)

    def __init__(self, name, config):
        self.name = name
        self.config = config

        self.max_marks = config['max_marks']

    def run_preprocess(self, grading_runner, preprocess_kwargs):
        state = preprocess_kwargs['state']

        preprocess_result = grading_runner.rpc_call(
            'run_preprocess', self.name, preprocess_kwargs)

        state.clear()
        state.update(preprocess_result['state'])
        return preprocess_result

    def run_test(self, testing_runner, testing_kwargs):
        command = testing_kwargs['command']
        if isinstance(command, str):
            command = '/bin/bash -c {0!s}'.format(shlex.quote(command))

        rc, stdout, stderr, stdplex = testing_runner.exec_step(command)

        return {
            'rc': rc,
            'stdout': stdout,
            'stderr': stderr,
            'stdplex': stdplex,
        }

    def run_postprocess(self, grading_runner, postprocess_kwargs):
        state = postprocess_kwargs['state']

        postprocess_result = grading_runner.rpc_call(
            'run_postprocess', self.name, postprocess_kwargs)

        state.clear()
        state.update(postprocess_result['state'])
        return postprocess_result

    def grade(self, grading_runner, testing_runner,
              base_preprocess_kwargs):
        step_result = {
            'broken': True,
            'fail': True,
            'continue': False,
            'marks': 0,
            'max_marks': self.max_marks,
            'output_msg': 'Grading failed, please contact your teacher!',
        }

        try:
            state = base_preprocess_kwargs['state']

            preprocess_kwargs = base_preprocess_kwargs.copy()
            preprocess_result = self.run_preprocess(
                grading_runner, preprocess_kwargs)

            step_result['continue'] = not preprocess_result['stop_on_failure']
            step_result['preprocess_result'] = preprocess_result

            testing_kwargs = preprocess_result.copy()
            testing_result = self.run_test(testing_runner, testing_kwargs)
            step_result['testing_result'] = testing_result

            try:
                testing_result['stdout'] = \
                    testing_result['stdout'].decode('ascii')

                testing_result['stderr'] = \
                    testing_result['stderr'].decode('ascii')

                testing_result['stdplex'] = \
                    testing_result['stdplex'].decode('ascii')
            except UnicodeError:
                step_result['output_msg'] = (
                    "You have non-ascii characters in your output. "
                    "You are probably reading/writing to memory, "
                    "which you don't control.")
                step_result['broken'] = False

                return step_result

            postprocess_kwargs = testing_result.copy()
            postprocess_kwargs['state'] = state
            postprocess_result = self.run_postprocess(
                grading_runner, postprocess_kwargs)
            step_result['postprocess_result'] = postprocess_result

            if postprocess_result['fail'] is False:
                step_result['fail'] = False
                step_result['continue'] = True
                step_result['marks'] = (postprocess_result['grade'] *
                                        self.max_marks // 100)

            step_result['output_msg'] = postprocess_result['output_msg']
            step_result['broken'] = False
        except:
            logger.exception('Uncaught exception while grading')

        return step_result


class Task:
    @classmethod
    def from_dir(cls, task_definition_dir):
        task_name = os.path.basename(os.path.normpath(task_definition_dir))
        task_definition_file = os.path.join(task_definition_dir, 'info.yaml')

        with open(task_definition_file) as f:
            definition = ordered_load(f)
            input_steps = definition['steps']

        steps = OrderedDict()
        for step_name, step_config in input_steps.items():
            step = TaskStep.from_dir(task_definition_dir,
                                     step_name, step_config)

            steps[step.name] = step

        grading_tag = '{0!s}/grading'.format(task_name)
        testing_tag = '{0!s}/testing'.format(task_name)

        grading_tag = docker_image_build(
            grading_tag, 'Dockerfile.grading', task_definition_dir)

        testing_tag = docker_image_build(
            testing_tag, 'Dockerfile.testing', task_definition_dir)

        return cls(grading_tag, testing_tag, steps)

    def __init__(self, grading_image, testing_image, steps):
        self.grading_image = grading_image
        self.testing_image = testing_image
        self.steps = steps

        max_marks = 0
        for step in steps.values():
            max_marks += step.max_marks

        self.max_marks = max_marks

    def grade(self, test_file_path):
        grading_image = self.grading_image
        testing_image = self.testing_image

        state = {}

        with GradingRunner(grading_image) as grading_runner, \
                TestingRunner(testing_image, test_file_path) as testing_runner:
            base_preprocess_kwargs = {
                'filename': testing_runner.input_file_container_path,
                'state': state,
            }

            for step in self.steps.values():
                step_result = step.grade(grading_runner, testing_runner,
                                         base_preprocess_kwargs)
                yield step.name, step_result

                if step_result['continue'] is False:
                    break
