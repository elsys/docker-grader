import os

from .settings import *  # noqa
from .settings import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5ub0vn1+wu$s-19sk@47f+=_3mdwcgcqs9wlx6c6q&6z)e1h&-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

WSGI_APPLICATION = 'grader.dev_wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CUSTOM
GRADER_SUBMISSIONS_DIR = os.path.join(BASE_DIR, 'submissions')
