from django.conf.urls import url

from . import views
from .views import TaskView, SubmissionsView, SubmissionsDataView
from .views import GradesView

urlpatterns = [
    url(r'^grades/$', GradesView.as_view(), name='grades'),
    url(r'^tasks/(?P<task_id>\d+)/$', TaskView.as_view(), name='task'),
    url(r'^submissions/(?P<task_id>\d+)/(?P<user_id>\d+)/$',
        SubmissionsView.as_view(),
        name='task-submissions'),
    url(r'^submissions_data/(?P<task_id>\d+)/(?P<user_id>\d+)/$',
        SubmissionsDataView.as_view(),
        name='task-submissions'),
    url(r'^download/(?P<submission_id>\d+)/$', views.download, name='download'),
    url(r'^download_mine/(?P<submission_id>\d+)/$', views.download_mine, name='download_mine'),
    url(r'^download_all/(?P<task_id>\d+)/$', views.download_all_for_task, name='download_all_for_task'),
]
