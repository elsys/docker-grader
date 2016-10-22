import os

from .settings import *  # noqa
from .settings import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR, 'local_settings/key.txt'), 'r') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'grader.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file':
                os.path.join(BASE_DIR, 'local_settings/my.cnf'),
        },
    }
}

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
