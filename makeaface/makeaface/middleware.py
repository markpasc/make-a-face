import logging

from django.http import HttpResponse


log = logging.getLogger(__name__)


class FixSecureRequestBustednessMiddleware(object):

    def process_response(self, request, response):
        if not isinstance(response, HttpResponse):
            log.debug("Response is a %r; not fixing", type(response))
            return response
        if response.status_code != 200:
            log.debug("Response's status is %r; not fixing", response.status_code)
            return response

        content_type = response['content-type']
        if not content_type.startswith('text/html'):
            log.debug("Response's content type is %r; not fixing", content_type)
            return response

        content = response.content
        content = content.replace('https://www.typepad.com/.s/', 'http://')

        return HttpResponse(content, status=response.status_code,
            content_type=content_type)
