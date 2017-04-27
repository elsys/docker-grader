from django.core.management.base import BaseCommand, CommandError
from tasks.models import Task
from lxml import etree

class Command(BaseCommand):
    help = 'Dumps task into file filename.yaml'
    args = '<task-slug> <filename>'


    def prettify_source(self, source):
        return "\n" + source.replace("\r\n","\n") + "\n"

    def prepare_step(self, step, step_el):
        etree.SubElement(step_el, "input").text = self.prettify_source(step.input_source)
        etree.SubElement(step_el, "output").text = self.prettify_source(step.output_source)

    def handle(self, *args, **options):
        task = Task.objects.get(slug=args[0])

        task_el = etree.Element("task")
        etree.SubElement(task_el, "id").text=task.slug
        etree.SubElement(task_el, "docker_image").text=task.docker_image
        etree.SubElement(task_el, "description").text=task.description

        steps_el = etree.SubElement(task_el, "steps")

        for step in task.steps.order_by("order"):
            step_el = etree.SubElement(steps_el, "step")
            self.prepare_step(step, step_el)

        tree = etree.ElementTree(task_el)
        tree.write(args[1], pretty_print = True)
