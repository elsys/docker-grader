from __future__ import absolute_import

from celery import shared_task
from docker import Client
from tasks.models import TaskSubmission


@shared_task
def grade(submission_id):
    submission = TaskSubmission.objects.get(pk=submission_id)

    runner = TaskRunner(submission.task.docker_image, submission.get_submission_path())
    res = ""
    for step in submission.task.steps.order_by("order"):
        res = runner.exec_step(step.input_source)
        print(res)
    return res


class DockerRunner:
    def __init__(self, docker_image, input_file, command):
        self.cli = Client(base_url="unix://var/run/docker.sock")
        self.container = self.cli.create_container(
            image=docker_image,
            command=command,
            stdin_open=True,
            host_config=self.cli.create_host_config(binds=[
                input_file + ":/mnt/input"
            ])
        )
        self.cli.start(self.container)


class TaskRunner(DockerRunner):
    def __init__(self, docker_image, input_file):
        DockerRunner.__init__(self, docker_image, input_file, "/bin/bash")

    def exec_step(self, command):
        ex = self.cli.exec_create(container=self.container,
                                  cmd=command, stdout=True, stderr=True)
        res = self.cli.exec_start(ex)
        return res


class GradingStepsRunner(DockerRunner):
    def __init__(self):
        DockerRunner.__init__(self, "python:latest", "rpc.py", "python /mnt/input")
