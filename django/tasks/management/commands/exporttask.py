from django.core.management.base import BaseCommand, CommandError
from tasks.models import Task
from lxml import etree

class Command(BaseCommand):
    help = 'Dumps task into file filename'
    args = '<task-slug> <filename>'

    def prettify_source(self, source):
        return "\n" + source.replace("\r\n","\n").strip() + "\n"

    def handle(self, *args, **options):
        task = Task.objects.get(slug=args[0])

        with open(args[1], 'w') as outfile:
            for step in task.steps.order_by("order"):
                outfile.write("#-----INPUT-TASK-STEP-----")
                outfile.write(self.prettify_source(step.input_source))
                outfile.write("#-----OUTPUT-TASK-STEP-----")
                outfile.write(self.prettify_source(step.output_source))
