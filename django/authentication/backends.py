import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from lti.contrib.django import DjangoToolProvider
from oauthlib.oauth1 import RequestValidator


logger = logging.getLogger(__name__)


class LTIValidator(RequestValidator):
    enforce_ssl = False

    def validate_timestamp_and_nonce(self, timestamp, nonce, request,
                                     request_token=None,
                                     access_token=None):
        return True

    def validate_client_key(self, client_key, request):
        return True

    def get_client_secret(self, client_key, request):
        return settings.LTI_OAUTH_CREDENTIALS.get(client_key)

    def check_client_key(self, client_key):
        return True

    def check_nonce(self, nonce):
        return True


class LTIAuthBackend(ModelBackend):

    def authenticate(self, request):
        request_key = request.POST.get('oauth_consumer_key', None)

        if request_key is None:
            logger.error("Request doesn't contain an oauth_consumer_key; can't continue.")
            return None

        if not settings.LTI_OAUTH_CREDENTIALS:
            logger.error("Missing LTI_OAUTH_CREDENTIALS in settings")
            raise PermissionDenied

        tool_provider = DjangoToolProvider.from_django_request(request=request)
        if not tool_provider.is_valid_request(LTIValidator()):
            raise PermissionDenied

        user = None

        # Retrieve username from LTI parameter or default to an overridable function return value
        username = tool_provider.ext_user_username

        email = tool_provider.lis_person_contact_email_primary
        first_name = tool_provider.lis_person_name_given
        last_name = tool_provider.lis_person_name_family

        UserModel = get_user_model()

        user, created = UserModel.objects.get_or_create(**{
            UserModel.USERNAME_FIELD: username,
        })

        # update the user
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        return user
