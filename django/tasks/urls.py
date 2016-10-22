from django.conf.urls import url

from .views import TaskView

urlpatterns = [
    url(r'^tasks/(?P<task_id>\d+)/$', TaskView.as_view(), name='task'),
]
