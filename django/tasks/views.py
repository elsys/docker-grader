import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse

from .models import Task
from .models import TaskSubmission
from .models import TaskLog

from .forms import TaskForm
from tasks import tasks


class TaskView(View):
    form_class = TaskForm
    template_name = 'task.html'

    @method_decorator(login_required)
    def dispatch(self, request, task_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id)

    def get(self, request, task_id):
        form = self.form_class()

        return self.display_page(request, form)

    def post(self, request, task_id):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            self.make_submission(request.user, request.FILES['zip_file'])

        return self.display_page(request, form, status=200)

    def display_page(self, request, form, status=200):
        context = {
            'form': form,
            'task': self.task,
        }
        return render(request, self.template_name, context, status=status)

    def make_submission(self, user, f):
        task_dir = self.task.get_task_dir()
        os.makedirs(task_dir, mode=0o2777, exist_ok=True)

        submission = TaskSubmission.objects.create(
            task=self.task, user=user)
        file_dir = submission.get_submission_path()

        with open(file_dir, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        TaskLog.objects.create(
            task_submission=submission, action=TaskLog.LOG_TYPE.SUBMITTED)
        tasks.grade.delay(submission.id)


class SubmissionsView(View):
    @method_decorator(login_required)
    def dispatch(self, request, task_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id)

    def get(self, request, task_id):
        submissions = self.task.submissions.filter(user=request.user)
        result = []
        for submission in submissions:
            result.append({"grade": submission.grade, "logs": list(submission.log.all().values())})
        return JsonResponse(result, safe=False)
