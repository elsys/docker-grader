from django.conf.urls import include, url
from django.contrib import admin

import tasks.urls
import teachers.urls

urlpatterns = [
    url(r'^', include(tasks.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^teachers/', include(teachers.urls)),
]
