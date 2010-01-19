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


CELL_WIDTH = 150
CELL_PAD = 4


def next_box_loc():
    """Generate the placements of 1x1 boxes beyond the 3x3 box in the upper
    left of the page."""
    for row in xrange(0, 3):
        for phile in xrange(0, 3):
            yield {
                'row': row,
                'file': phile,
                'rowlast': True if phile == 2 else False,
            }
    row = 3
    while True:
        for phile in xrange(0, 6):
            yield {
                'row': row,
                'file': phile,
                'rowlast': True if phile == 5 else False,
            }
        row += 1


def home(request):
    with typepad.client.batch_request():
        events = request.group.events

    import logging
    logging.debug(request.user)

    return TemplateResponse(request, 'makeaface/home.html', {
        'events': events,
        'next_box_loc': next_box_loc(),
    })


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
    loc = loc_parts['asset_url'][0]

    logging.critical('LOCATION IS A %s %r', type(loc).__name__, loc)
    with typepad.client.batch_request():
        asset = typepad.api.Asset.get(loc)
    image_url = asset.links['maxwidth__150'].href[:-6] + '-150si'

    # Flash doodad needs a 200, not a redirect.
    return HttpResponse(image_url, content_type='text/plain')


@oops
def favorite(request):
    if request.method != 'POST':
        return HttpResponse('POST required at this url', status=400, content_type='text/plain')

    action = request.POST.get('action', 'favorite')
    asset_id = request.POST.get('asset_id')
    if not asset_id:
        raise Http404

    if action == 'favorite':
        with typepad.client.batch_request():
            asset = typepad.Asset.get_by_url_id(asset_id)
        fav = typepad.Favorite()
        fav.in_reply_to = asset.asset_ref
        request.user.favorites.post(fav)
    else:
        with typepad.client.batch_request():
            fav = typepad.Favorite.get_by_user_asset(request.user.xid, asset_id)
        fav.delete()

    return HttpResponse('OK', content_type='text/plain')
