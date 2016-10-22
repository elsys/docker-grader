"""
Django settings for grader project.

Generated by 'django-admin startproject' using Django 1.8.15.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

MY_APPS = (
    'authentication',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
) + MY_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'grader.urls'

TEMPLATES = [
]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# CUSTOM
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(process)d %(thread)d '
                      '%(name)s %(pathname)s:%(lineno)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'django-default': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django-default.log'),
            'formatter': 'verbose',
        },
        'grader-default': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/grader-default.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django-default'],
            'level': 'INFO',
            'propagate': True,
        },
        'grader': {
            'handlers': ['console', 'grader-default'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

APPEND_SLASH = False
PREPEND_WWW = False
USE_ETAGS = True
AUTH_USER_MODEL = 'authentication.User'

EMAIL_SUBJECT_PREFIX = '[ELSYS] '
DEFAULT_FROM_EMAIL = 'ELSYS Grader <grader@elsys-bg.org>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = tuple()
MANAGERS = ADMINS


REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'URL_FORMAT_OVERRIDE': None,
}

LOGIN_URL = '/login'