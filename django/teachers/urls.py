from django.conf.urls import url

from . import views
from .views import TaskView, SubmissionsView, SubmissionsDataView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tasks/(?P<task_id>\d+)/$', TaskView.as_view(), name='task'),
    url(r'^submissions/(?P<task_id>\d+)/(?P<user_id>\d+)/$',
        SubmissionsView.as_view(),
        name='task-submissions'),
    url(r'^submissions_data/(?P<task_id>\d+)/(?P<user_id>\d+)/$',
        SubmissionsDataView.as_view(),
        name='task-submissions'),
]
