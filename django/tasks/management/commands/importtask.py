from django.core.management.base import BaseCommand
from tasks.models import Task, TaskStep


class Command(BaseCommand):
    help = 'Dumps task into file filename'
    args = '<task-slug> <docker-image> <filename>'

    def handle(self, *args, **options):
        inputs = []
        outputs = []

        with open(args[2], 'r') as infile:
            currentBuffer = ""

            for line in infile:
                if line.strip() == "#-----INPUT-TASK-STEP-----":
                    if currentBuffer != "":
                        outputs.append(currentBuffer)
                    currentBuffer = ""
                elif line.strip() == "#-----OUTPUT-TASK-STEP-----":
                    if currentBuffer != "":
                        inputs.append(currentBuffer)
                    currentBuffer = ""
                else:
                    currentBuffer += line

            if currentBuffer != "":
                outputs.append(currentBuffer)

        task = Task.objects.create(slug=args[0], docker_image=args[1])
        for i, (input_code, output_code) in enumerate(zip(inputs, outputs)):
            TaskStep.objects.create(order=i, task=task,
                                    input_source=input_code,
                                    output_source=output_code)
