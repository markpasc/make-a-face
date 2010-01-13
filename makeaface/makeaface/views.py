from __future__ import with_statement

from cgi import parse_qs
from cStringIO import StringIO
import functools
import logging
from urlparse import urlparse

from django.http import HttpResponse, HttpResponseRedirect
from templateresponse import TemplateResponse
import typepad
import typepad.api


def oops(fn):
    @functools.wraps(fn)
    def hoops(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, exc:
            logging.exception(exc)
            return HttpResponse('%s: %s' % (type(exc).__name__, str(exc)), status=400, content_type='text/plain')
    return hoops


def home(request):
    with typepad.client.batch_request():
        events = request.group.events

    import logging
    logging.debug(request.user)

    return TemplateResponse(request, 'makeaface/home.html',
        {'events': events})


@oops
def upload_photo(request):
    if request.method != 'POST':
        return HttpResponse('POST required at this url', status=400, content_type='text/plain')

    content_type = request.META['CONTENT_TYPE']
    assert content_type.startswith('image/')
    bodyfile = StringIO(request.raw_post_data)

    asset = typepad.api.Asset()
    resp, content = typepad.api.browser_upload.upload(asset, bodyfile,
        content_type=content_type, redirect_to='http://example.com/')

    if resp.status != 302:
        logging.debug('%d response from typepad: %s', resp.status, content)
    assert resp.status == 302

    if 'location' not in resp:
        logging.debug('No Location in response, only %r', resp.keys())
    loc = resp['location']
    loc_parts = parse_qs(urlparse(loc).query)
    loc = loc_parts['asset_url']

    # Flash doodad needs a 200, not a redirect.
    return HttpResponse(loc, content_type='text/plain')
