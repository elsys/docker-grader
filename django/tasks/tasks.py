from __future__ import absolute_import

import os
from celery import shared_task
from docker import Client
from tasks.models import TaskSubmission
from django.conf import settings


@shared_task
def grade(submission_id):
    submission = TaskSubmission.objects.get(pk=submission_id)

    with GradingStepsRunner(), TaskRunner(submission.task.docker_image, submission.get_submission_path()) as runner:
        res = ""
        for step in submission.task.steps.order_by("order"):
            res = runner.exec_step(step.input_source)
            print(res)
    return res


class DockerRunner:
    def __init__(self):
        self.cli = Client(base_url="unix://var/run/docker.sock")

    def stop(self):
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
