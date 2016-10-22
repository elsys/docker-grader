from __future__ import absolute_import

from celery import shared_task
from docker import Client


@shared_task
def grade(filename):
    runner = TaskRunner("gcc:latest", filename)
    runner.exec_step("gcc -x c /mnt/input")
    res = runner.exec_step("./a.out")
    return res


class TaskRunner:
    def __init__(self, docker_image, input_file):
        self.cli = Client(base_url='unix://var/run/docker.sock')
        self.container = self.cli.create_container(
            image=docker_image,
            command='/bin/bash',
            stdin_open=True,
            host_config=self.cli.create_host_config(binds=[
                input_file + ':/mnt/input'
            ])
        )
        self.cli.start(self.container)

    def exec_step(self, command):
        ex = self.cli.exec_create(container=self.container,
                                  cmd=command, stdout=True, stderr=True)
        res = self.cli.exec_start(ex)
        return res
