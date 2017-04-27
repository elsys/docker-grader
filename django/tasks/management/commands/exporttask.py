from django.core.management.base import BaseCommand, CommandError
from tasks.models import Task
import yaml

class literal_str(str): pass

def literal_str_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(literal_str, literal_str_representer)

class Command(BaseCommand):
    help = 'Dumps task into file filename.yaml'
    args = '<task-slug> <filename>'


    def prepare_step(self, step):
        return {
            "input_source": literal_str(step.input_source),
            "output_source": literal_str(step.output_source)
        }

    def handle(self, *args, **options):
        task = Task.objects.get(slug=args[0])
        steps = [self.prepare_step(step) for step in task.steps.order_by("order")]

        task_dict = {
            "id": task.slug,
            "docker_image": task.docker_image,
            "description": task.description,
            "steps": steps
        }

        with open(args[1], 'w') as stream:
            yaml.dump(task_dict, stream)
