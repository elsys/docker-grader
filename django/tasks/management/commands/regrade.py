import time

from django.core.management.base import BaseCommand, CommandError
from tasks.models import TaskSubmission


class Command(BaseCommand):
    help = 'Regrades all ungraded tasks'

    def handle(self, *args, **options):
        ungraded = TaskSubmission.objects.filter(grading_completed=False)
        i = 1
        count = ungraded.count()
        for submission in ungraded:
            self.stdout.write('Regrading submission {} ({}/{}).'.format(submission, i, count))
            submission.regrade()
            # time.sleep(40)
            i += 1
