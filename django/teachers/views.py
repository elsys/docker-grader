from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View
from tasks.models import Task
from django.db.models import Max

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class TaskView(View):
    template_name = 'submissions.html'

    #@staff_member_required
    def dispatch(self, request, task_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id)

    def get(self, request, task_id):
        context = {
            'submissions': self.task.submissions.values('user__username').annotate(grade=Max('grade'))
        }
        return render(request, self.template_name, context, status=200)
