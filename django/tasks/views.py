from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect

from .forms import TaskForm


class TaskView(View):
    form_class = TaskForm
    template_name = 'task.html'

    def get(self, request, task_id):
        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, task_id):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            return HttpResponseRedirect('/')

        return render(request, self.template_name, {'form': form}, status=400)
