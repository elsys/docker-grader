from __future__ import absolute_import

import os
import xmlrpc.client
import time
from celery import shared_task
from docker import Client
from tasks.models import TaskSubmission, TaskLog
from django.conf import settings
from celery.exceptions import SoftTimeLimitExceeded


@shared_task
def grade(submission_id):
    submission = TaskSubmission.objects.get(pk=submission_id)
    state = "/mnt/input"
    grade = 0

    with GradingStepsRunner(), TaskRunner(submission.task.docker_image, submission.get_submission_path()) as runner:
        rpc = xmlrpc.client.ServerProxy('http://localhost:7799')
        time.sleep(1)

        for step in submission.task.steps.order_by("order"):
            input_result = rpc.prepare_input_command(step.input_source, state)
            execution_result = runner.exec_step(input_result["command"])
            output_result = rpc.parse_output(step.output_source, input_result["state"], execution_result, "", 0)
            state = output_result["state"]
            grade = grade + output_result["grade"]
            TaskLog.objects.create(task_submission=submission,
                                   action=TaskLog.LOG_TYPE.STEP_COMPLETED,
                                   extra=output_result["output_msg"])
            if not output_result["exec_next_step"]:
                break
    submission.grade = grade
    submission.grading_completed = True
    submission.save()
    return state


class DockerRunner:
    def __init__(self):
        self.cli = Client(base_url="unix://var/run/docker.sock")

    def stop(self):
        self.cli.kill(self.container)
        self.cli.stop(self.container)
        self.cli.remove_container(self.container)

    def __enter__(self):
        self.cli.start(self.container)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class TaskRunner(DockerRunner):
    def __init__(self, docker_image, input_file):
        DockerRunner.__init__(self)
        self.container = self.cli.create_container(
            image=docker_image,
            command="/bin/bash",
            stdin_open=True,
            host_config=self.cli.create_host_config(
                binds=[input_file + ":/mnt/input"],
                privileged=False,
                network_mode='none',
                mem_limit="100M",
                memswap_limit="100M",
                shm_size="100M",
                kernel_memory="50M",
                pids_limit=100,
            )
        )

    def exec_step(self, command):
        ex = self.cli.exec_create(container=self.container,
                                  cmd=command, stdout=True, stderr=True)
        res = self.cli.exec_start(ex)
        return res


class GradingStepsRunner(DockerRunner):
    def __init__(self):
        DockerRunner.__init__(self)
        self.container = self.cli.create_container(
            image="python:latest",
            command="python /mnt/input",
            stdin_open=True,
            ports=[8000],
            host_config=self.cli.create_host_config(
                binds=[self.get_python_rpc_source_path() + ":/mnt/input"],
                port_bindings={8000: 7799}
            )
        )

    @staticmethod
    def get_python_rpc_source_path():
        return os.path.join(settings.BASE_DIR, "tasks", "rpc.py")
