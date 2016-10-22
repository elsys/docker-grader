import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect

from .models import Task
from .models import TaskSubmission

from .forms import TaskForm


class TaskView(View):
    form_class = TaskForm
    template_name = 'task.html'

    def get(self, request, task_id):
        get_object_or_404(Task, id=task_id)

        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            self.save_file(task, request.FILES['zip_file'])
            return HttpResponseRedirect('/')

        return render(request, self.template_name, {'form': form}, status=400)

    def save_file(self, task, f):
        task_dir = task.get_task_dir()
        os.makedirs(task_dir, mode=0o2777, exist_ok=True)

        submission = TaskSubmission.objects.create(task=task, user=None)
        file_dir = submission.get_submission_path()

        with open(file_dir, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
