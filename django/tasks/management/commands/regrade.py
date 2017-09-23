from django.core.management.base import BaseCommand
from tasks.models import TaskSubmission


class Command(BaseCommand):
    help = 'Regrades all ungraded tasks'

    def handle(self, *args, **options):
        ungraded = TaskSubmission.objects.filter(grading_completed=False)
        i = 1
        count = ungraded.count()
        for submission in ungraded:
            self.stdout.write('Regrading submission {} ({}/{}).'.format(
                submission, i, count))
            submission.regrade()
            i += 1
