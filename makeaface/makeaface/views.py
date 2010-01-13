from __future__ import with_statement

import functools

from templateresponse import TemplateResponse
import typepad
import typepadapp.views.base
import motion.views


def home(request):
    with typepad.client.batch_request():
        events = request.group.events

    import logging
    logging.debug(request.user)

    return TemplateResponse(request, 'makeaface/home.html',
        {'events': events})


def upload_photo(request):
    if request.method != 'POST':
        raise HttpResponse('POST required at this url', status=400, content_type='text/plain')

    assert request.META['CONTENT_TYPE'].startswith('image/jpeg')
    body = request.raw_post_data

    # dur de dur
    url = 'hur'

    return HttpResponseRedirect('YAY', content_type='text/plain')
