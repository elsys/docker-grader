from django.conf.urls import url

from . import views
from .views import TaskView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tasks/(?P<task_id>\d+)/$', TaskView.as_view(), name='task'),
]
