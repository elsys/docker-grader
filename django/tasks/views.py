from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from .models import Task
from .models import TaskSubmission

from .forms import TaskForm


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
            TaskSubmission.objects.submit_submission(
                self.task, request.user, form.cleaned_data['submission'])
            return HttpResponseRedirect(request.get_full_path())

        return self.display_page(request, form, status=400)

    def display_page(self, request, form, status=200):
        context = {
            'form': form,
            'data_url': "/submissions/" + str(self.task.id) + "/",
            'task': self.task,
        }
        return render(request, self.template_name, context, status=status)


class SubmissionsView(View):
    @method_decorator(login_required)
    def dispatch(self, request, task_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id)

    def get(self, request, task_id):
        submissions = self.task.submissions.filter(user=request.user)
        result = []
        for submission in submissions:
            result.append({"grade": submission.grade,
                           "id": submission.id,
                           "logs": list(submission.log.all().values())})
        return JsonResponse(result, safe=False)
