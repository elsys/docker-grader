import logging

from django.contrib import auth
from django.http import HttpResponseRedirect


logger = logging.getLogger(__name__)


class LTIAuthMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and request.POST.get('lti_message_type') == 'basic-lti-launch-request':
            logger.debug('received a basic-lti-launch-request - authenticating the user')

            # authenticate and log the user in
            user = auth.authenticate(request=request)

            if user is not None:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.

                logger.debug('user was successfully authenticated; now log them in')
                request.user = user
                auth.login(request, user)
                return HttpResponseRedirect(request.get_full_path())
