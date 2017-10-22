from django.core.management.base import BaseCommand

from grader.base.task import Task as MemTask

from tasks.models import Task


class Command(BaseCommand):
    help = 'Import test task from dir'

    def add_arguments(self, parser):
        parser.add_argument('task_slug', type=str)
        parser.add_argument('task_definition_dir', type=str)

    def handle(self, task_slug, task_definition_dir, *args, **options):
        self.stdout.write(
            "Reading task definition from directory... ", ending='')
        mem_task = MemTask.from_dir(task_definition_dir)
        self.stdout.write(self.style.SUCCESS("Done."))

        self.stdout.write(
            "Importing task definition to database... ", ending='')
        Task.from_mem_task(mem_task, task_slug)
        self.stdout.write(self.style.SUCCESS("Done."))
