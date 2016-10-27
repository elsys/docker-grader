from django.conf.urls import url

from .views import TaskView, SubmissionsView

urlpatterns = [
    url(r'^tasks/(?P<task_id>\d+)/$', TaskView.as_view(), name='task'),
    url(r'^submissions/(?P<task_id>\d+)/$', SubmissionsView.as_view(), name='task'),
]
