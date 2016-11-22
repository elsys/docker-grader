from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View
from tasks.models import Task, TaskSubmission
from django.db.models import Max
from django.http import JsonResponse
from django.utils.encoding import smart_str
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@staff_member_required
def download(request, submission_id):
    submission = TaskSubmission.objects.get(pk=submission_id)
    file_name = submission.task.slug + "_" + submission.user.username + "_" + submission_id
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = smart_str(submission.get_submission_path())
    return response

class TaskView(View):
    template_name = 'submissions.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, task_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id)

    def get(self, request, task_id):
        context = {
            'data_url': "/teachers/submissions/" + task_id,
            'submissions': self.task.submissions.values('user', 'user__username').annotate(grade=Max('grade'))
        }
        return render(request, self.template_name, context, status=200)


class SubmissionsView(View):
    template_name = 'task.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, task_id, user_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id, user_id)

    def get(self, request, task_id, user_id):
        context = {
            'data_url': "/teachers/submissions_data/" + task_id + "/" + user_id + "/",
        }
        return render(request, self.template_name, context, status=200)

class SubmissionsDataView(View):
    @method_decorator(staff_member_required)
    def dispatch(self, request, task_id, user_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id, user_id)

    def get(self, request, task_id, user_id):
        submissions = self.task.submissions.filter(user=user_id)
        result = []
        for submission in submissions:
            result.append({"grade": submission.grade, "id": submission.id, "logs": list(submission.log.all().values())})
        return JsonResponse(result, safe=False)
