import os
from urllib.parse import urljoin

from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.conf import settings
from django.db.models import Max
from django.http import JsonResponse
from django.utils.encoding import smart_str
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from tasks.models import Task, TaskSubmission, TaskLog
from django.template.defaulttags import register
from datetime import datetime


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def get_submission_uri_from_path(path):
    base = urljoin(settings.STATIC_URL, 'submissions/')
    return urljoin(base,
                   os.path.relpath(path, settings.GRADER_SUBMISSIONS_DIR))


@login_required
def download_mine(request, submission_id):
    submission = TaskSubmission.objects.get(pk=submission_id)
    date = submission.log.filter(action=TaskLog.LOG_TYPE.SUBMITTED).get().date
    limit = datetime(2018, 4, 13, 0, 0, 0, tzinfo=date.tzinfo)
    if submission.user != request.user or date > limit:
        return HttpResponse('Unauthorized', status=401)
    file_name = submission.task.slug + "_" + submission.user.username + "_" + submission_id
    path = smart_str(submission.get_submission_path())

    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = path
    response['X-Accel-Redirect'] = get_submission_uri_from_path(path)
    return response


@staff_member_required
def download(request, submission_id):
    submission = TaskSubmission.objects.get(pk=submission_id)
    file_name = submission.task.slug + "_" + submission.user.username + "_" + submission_id
    path = smart_str(submission.get_submission_path())

    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = path
    response['X-Accel-Redirect'] = get_submission_uri_from_path(path)
    return response


@staff_member_required
def download_all_for_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    best_dir = os.path.join(task.get_task_dir(), "best")
    os.makedirs(best_dir, mode=0o2777, exist_ok=True)

    best_submission = None
    current_user = None

    for submission in task.submissions.order_by("user", "id"):
        if submission.user != current_user:
            current_user = submission.user
            if best_submission != None:
                user_dir = os.path.join(best_dir, best_submission.user.username)
                os.makedirs(user_dir, mode=0o2777, exist_ok=True)
                command = "unzip " + best_submission.get_submission_path() + " -d " + user_dir + " || " \
                          "tar -zxvf " + best_submission.get_submission_path() + " -C " + user_dir
                os.system(command)
            best_submission = None
        if best_submission == None or submission.grade >= best_submission.grade:
            best_submission = submission

    if best_submission != None:
        user_dir = os.path.join(best_dir, best_submission.user.username)
        os.makedirs(user_dir, mode=0o2777, exist_ok=True)
        command = "unzip " + best_submission.get_submission_path() + " -d " + user_dir + " || " \
                  "tar -zxvf " + best_submission.get_submission_path() + " -C " + user_dir
        os.system(command)

    best_archive = os.path.join(task.get_task_dir(), "best.tar.gz")
    os.system("tar -cvzf " + best_archive + " -C " + best_dir + " .")

    file_name = submission.task.slug + "_best.tar.gz"
    path = smart_str(best_archive)

    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = path
    response['X-Accel-Redirect'] = get_submission_uri_from_path(path)
    return response


class TaskView(View):
    template_name = 'submissions.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request, task_id):
        self.task = get_object_or_404(Task, id=task_id)

        return super().dispatch(request, task_id)

    def get(self, request, task_id):
        context = {
            'task_id': task_id,
            'data_url': "/teachers/submissions/" + task_id,
            'submissions': self.task.submissions
                                    .values('user', 'user__username', 'user__first_name', 'user__last_name')
                                    .annotate(grade=Max('grade'))
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
            result.append({"grade": submission.grade,
                           "id": submission.id,
                           "logs": list(submission.log.all().values())})
        return JsonResponse(result, safe=False)


class GradesView(View):
    template_name = 'grades.html'
    
    @method_decorator(staff_member_required)
    def get(self, request):
        tasks = Task.objects.all().values("slug", "id")
        grades = []
        
        for username in get_user_model().objects.all().values_list('username', flat=True):
            user_grades = { 'username': username }
            for grade in TaskSubmission.objects.filter(user__username=username).values('task_id').annotate(grade=Max('grade')):
                user_grades[grade['task_id']] = grade['grade']
            grades.append(user_grades)
            
        context = {
            'grades': grades,
            'tasks': tasks
        }
        return render(request, self.template_name, context, status=200)
