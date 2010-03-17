from __future__ import with_statement

from cgi import parse_qs
from cStringIO import StringIO
import functools
import logging
import re
from urlparse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve
import django.db.models.signals
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from oauth.oauth import OAuthConsumer, OAuthToken
import simplejson as json
from templateresponse import TemplateResponse
import typepad
import typepad.api
import typepadapp.signals
from typepadapp.models import Asset, Favorite, Photo, User

from makeaface.models import Lastface, Favoriteface


log = logging.getLogger(__name__)

ONE_DAY = 86400


def oops(fn):
    @functools.wraps(fn)
    def hoops(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, exc:
            log.exception(exc)
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


def home(request, page=None, template=None):
    authed = request.user.is_authenticated()

    elsewhere = None
    with typepad.client.batch_request():
        events = request.group.events

        if page is not None:
            page = int(page)
            start_index = 50 * (page - 1) + 1
            events = events.filter(max_results=50, start_index=start_index)
        else:
            page = 0

        if authed:
            elsewhere = request.user.elsewhere_accounts

    if authed:
        elsewhere = sharing_for_elsewhere(elsewhere)

    user_agent = request.META['HTTP_USER_AGENT']
    log.debug('User agent is %r', user_agent)

    if template is None:
        template = 'makeaface/home.html'
    return TemplateResponse(request, template, {
        'events': events,
        'next_box_loc': next_box_loc(),
        'share': elsewhere,
        'next_page': page + 1,
        'prev_page': page - 1,
    })


@oops
def asset_meta(request, fresh=False):
    if not request.user.is_authenticated():
        return HttpResponse('silly rabbit, asset_meta is for authenticated users',
            status=400, content_type='text/plain')

    user_id = request.user.xid
    cache_key = 'favorites:%s' % user_id
    favs = None if fresh else cache.get(cache_key)

    if favs is None:
        log.debug("Oops, going to server for %s's asset_meta", request.user.preferred_username)

        fav_objs = {}
        html_ids = request.POST.getlist('asset_id')
        with typepad.client.batch_request():
            for html_id in html_ids:
                assert html_id.startswith('asset-')
                xid = html_id[6:]
                fav_objs[html_id] = Favorite.head_by_user_asset(user_id, xid)

        favs = list(html_id for html_id, fav_obj in fav_objs.items()
            if fav_obj.found())
        if not fresh:
            cache.set(cache_key, favs, ONE_DAY)
    else:
        log.debug('Yay, returning asset_meta for %s from cache', request.user.preferred_username)

    favs = dict((html_id, {"favorite": True}) for html_id in favs)
    return HttpResponse(json.dumps(favs), content_type='application/json')


def authorize(request):
    resp = typepadapp.views.auth.authorize(request)
    if isinstance(resp, HttpResponseRedirect):
        request.flash['signedin'] = True
    return resp


def noob(request):
    request.flash['signedin'] = True
    return HttpResponseRedirect(reverse('home'))


def sharing_for_elsewhere(ew):
    twitter, facebook = None, None
    for account in ew:
        if account.domain == 'twitter.com':
            twitter = account
        elif account.domain == 'facebook.com':
            facebook = account

    return ('Facebook' if facebook is not None
        else 'Twitter' if twitter is not None
        else 'TypePad')


def photo(request, xid):
    # Ask this up front to get the user object outside of batches.
    authed = request.user.is_authenticated()

    lastface, elsewhere = None, None
    with typepad.client.batch_request():
        photo = Asset.get_by_url_id(xid)
        favs = photo.favorites

        favfaces = dict()
        for face in Favoriteface.objects.all().filter(favorited=xid):
            favfaces[face.favoriter] = Asset.get_by_url_id(face.lastface)

        if authed:
            elsewhere = request.user.elsewhere_accounts
            try:
                lastface_mod = Lastface.objects.get(owner=request.user.xid)
            except Lastface.DoesNotExist:
                pass
            else:
                lastface = Asset.get_by_url_id(lastface_mod.face)

    userfav = None
    if authed:
        elsewhere = sharing_for_elsewhere(elsewhere)
        # Get the Favorite in a separate batch so we can handle if it fails.
        try:
            with typepad.client.batch_request():
                userfav = Favorite.get_by_user_asset(request.user.xid, xid)
        except Favorite.NotFound:
            userfav = None

    # Annotate the favorites with the last faces, so we get them naturally in their loop.
    for fav in favs:
        try:
            fav.lastface = favfaces[fav.author.xid]
        except KeyError:
            pass

    return TemplateResponse(request, 'makeaface/photo.html', {
        'photo': photo,
        'favorites': favs,
        'user_favorite': userfav,
        'lastface': lastface,
        'share': elsewhere,
    })


photo.is_photo_view = True


def oembed(request):
    # Ask this up front to get the user object outside of batches.
    authed = request.user.is_authenticated()

    url = request.GET['url']
    urlparts = urlparse(url)
    view, args, kwargs = resolve(urlparts.path)

    if not getattr(view, 'is_photo_view', False):
        return HttpResponseNotFound('not a photo url', content_type='text/plain')
    if request.GET.get('format', 'json') != 'json':
        return HttpResponse('unsupported format :(', status=501, content_type='text/plain')

    xid = kwargs['xid']
    maxwidth = request.GET.get('maxwidth')
    maxheight = request.GET.get('maxheight')
    if maxwidth and maxheight:
        size = maxwidth if maxwidth < maxheight else maxheight
    elif maxwidth:
        size = maxwidth
    elif maxheight:
        size = maxheight
    else:
        size = 500

    typepad.client.batch_request()
    photo = Asset.get_by_url_id(xid)
    try:
        typepad.client.complete_batch()
    except Asset.NotFound:
        return HttpResponseNotFound('no such photo', content_type='text/plain')

    photo_url = photo.links['rel__enclosure']['maxwidth__%d' % size].href

    data = {
        'type': 'photo',
        'version': '1.0',
        'title': "%s's face" % photo.author.display_name,
        'author_name': photo.author.display_name,
        'provider_name': 'Make A Face',
        'provider_url': 'http://make-a-face.org/',
        'url': photo_url,
        'width': size,
        'height': size,
    }
    if size > 150:
        data.update({
            'thumbnail_url': photo.links['rel__enclosure']['maxwidth__150'].href,
            'thumbnail_width': 150,
            'thumbnail_height': 150,
        })

    return HttpResponse(json.dumps(data), content_type='application/json+javascript')


@oops
def upload_photo(request):
    if request.method != 'POST':
        return HttpResponse('POST required at this url', status=400, content_type='text/plain')

    content_type = request.META['CONTENT_TYPE']
    assert content_type.startswith('image/')
    bodyfile = StringIO(request.raw_post_data)

    target_url = request.group.photo_assets._location
    target_parts = urlparse(target_url)
    target_path = target_parts.path.replace('.json', '')
    log.debug('Using %r as target URL', target_path)

    asset = Asset()
    asset.title = "a face"
    resp, content = typepad.api.browser_upload.upload(asset, bodyfile,
        content_type=content_type, redirect_to='http://example.com/',
        target_url=target_path)

    if resp.status != 302:
        log.debug('%d response from typepad: %s', resp.status, content)
    assert resp.status == 302

    typepadapp.signals.asset_created.send(sender=asset, instance=asset,
        group=request.group, parent=request.group.photo_assets)

    if 'location' not in resp:
        log.debug('No Location in response, only %r', resp.keys())
    loc = resp['location']
    loc_parts = parse_qs(urlparse(loc).query)

    if 'asset_url' not in loc_parts:
        log.warning('New location was %r', loc)
        log.warning('Original response/content were %r, %r', resp, content)
    loc = loc_parts['asset_url'][0]

    log.debug('LOCATION IS A %s %r', type(loc).__name__, loc)
    with typepad.client.batch_request():
        asset = Asset.get(loc)
    image_url = asset.links['maxwidth__150'].href[:-6] + '-150si'

    # Save the photo as a new last face for the poster.
    Lastface(owner=request.user.xid, face=asset.xid).save()

    # Flash doodad needs a 200, not a redirect.
    return HttpResponse(image_url, content_type='text/plain')


@oops
def favorite(request):
    if request.method != 'POST':
        return HttpResponse('POST required at this url', status=400, content_type='text/plain')

    action = request.POST.get('action', 'favorite')
    asset_id = request.POST.get('asset_id', '')
    try:
        (asset_id,) = re.findall('6a\w+', asset_id)
    except TypeError:
        raise Http404

    if action == 'favorite':
        with typepad.client.batch_request():
            asset = Asset.get_by_url_id(asset_id)
        fav = Favorite()
        fav.in_reply_to = asset.asset_ref
        request.user.favorites.post(fav)
        typepadapp.signals.favorite_created.send(sender=fav, instance=fav, parent=asset,
            group=request.group)

        # Save the user's last face when favorited.
        try:
            last = Lastface.objects.get(owner=request.user.xid)
        except Lastface.DoesNotExist:
            pass
        else:
            Favoriteface(favoriter=request.user.xid, favorited=asset_id,
                lastface=last.face).save()
    else:
        # Getting the xid will do a batch, so don't do it inside our other batch.
        xid = request.user.xid
        with typepad.client.batch_request():
            asset = Asset.get_by_url_id(asset_id)
            fav = Favorite.get_by_user_asset(xid, asset_id)
        fav.delete()
        typepadapp.signals.favorite_deleted.send(sender=fav, instance=fav,
            parent=asset, group=request.group)

    return HttpResponse('OK', content_type='text/plain')


def uncache_favorites(sender, instance, **kwargs):
    cache_key = 'favorites:%s' % instance.author.xid
    cache.delete(cache_key)


typepadapp.signals.favorite_created.connect(uncache_favorites)
typepadapp.signals.favorite_deleted.connect(uncache_favorites)


def uncache_lastface(sender, instance, **kwargs):
    cache_key = 'lastface:%s' % instance.owner
    cache.delete(cache_key)

django.db.models.signals.post_save.connect(uncache_lastface, sender=Lastface)
django.db.models.signals.post_delete.connect(uncache_lastface, sender=Lastface)


@oops
def flag(request):
    if request.method != 'POST':
        return HttpResponse('POST required at this url', status=400, content_type='text/plain')

    action = request.POST.get('action', 'flag')
    asset_id = request.POST.get('asset_id', '')
    try:
        (asset_id,) = re.findall('6a\w+', asset_id)
    except TypeError:
        raise Http404

    cache_key = 'flag:%s' % asset_id

    if action != 'flag':
        return HttpResponse('Only flag action is supported at this url', status=400, content_type='text/plain')

    # YAY UNATOMIC OPERATIONS
    flaggers = cache.get(cache_key)
    if not flaggers:
        log.debug('No flaggers for %r yet, making a new list', asset_id)
        flaggers = []
    elif request.user.xid in flaggers:
        log.debug('%r re-flagged %r (ignored)', request.user.xid, asset_id)
        return HttpResponse('OK (though you already flagged it)', content_type='text/plain')

    flaggers.append(request.user.xid)
    if len(flaggers) >= 3:
        log.debug('%r was the last straw for %r! Deleting!', request.user.xid, asset_id)
        with typepad.client.batch_request():

            # Re-authenticate the client with the superuser credentials that can delete that.
            typepad.client.clear_credentials()
            backend = urlparse(settings.BACKEND_URL)
            csr = OAuthConsumer(settings.OAUTH_CONSUMER_KEY, settings.OAUTH_CONSUMER_SECRET)
            token = OAuthToken(settings.OAUTH_SUPERUSER_KEY, settings.OAUTH_SUPERUSER_SECRET)
            typepad.client.add_credentials(csr, token, domain=backend[1])

            asset = Asset.get_by_url_id(asset_id)
            asset.delete()
            typepadapp.signals.asset_deleted.send(sender=asset, instance=asset,
                group=request.group)
            del asset  # lose our reference to it

            log.debug('BALEETED')

        cache.delete(cache_key)
        log.debug('Emptied flaggers for %r now that it is deleted', asset_id)
        return HttpResponse('BALEETED', content_type='text/plain')
    else:
        cache.set(cache_key, flaggers, ONE_DAY)
        log.debug('Flaggers for %r are now %r', asset_id, flaggers)
        return HttpResponse('OK', content_type='text/plain')


def cull_old_lastfavfaces(sender, instance, group, **kwargs):
    Lastface.objects.filter(face=instance.xid).delete()
    Favoriteface.objects.filter(lastface=instance.xid).delete()


typepadapp.signals.asset_deleted.connect(cull_old_lastfavfaces)


@oops
def delete(request):
    if request.method != 'POST':
        return HttpResponse('POST required at this url', status=400, content_type='text/plain')

    action = request.POST.get('action', 'delete')
    asset_id = request.POST.get('asset_id', '')
    try:
        (asset_id,) = re.findall('6a\w+', asset_id)
    except TypeError:
        raise Http404

    if action == 'delete':
        # Getting the xid will do a batch, so don't do it inside our other batch.
        xid = request.user.xid
        with typepad.client.batch_request():
            asset = Asset.get_by_url_id(asset_id)
        asset.delete()
        typepadapp.signals.asset_deleted.send(sender=asset, instance=asset,
            group=request.group)

    return HttpResponse('', status=204)


@oops
def lastface(request, xid, spec):
    cache_key = 'lastface:%s' % xid
    face = cache.get(cache_key)

    if face is None:
        try:
            face = Lastface.objects.get(owner=xid)
        except Lastface.DoesNotExist:
            # Get that person's userpic.
            with typepad.client.batch_request():
                user = User.get_by_url_id(xid)

            face = user.links['rel__avatar']['maxwidth__200'].href
            if 'default-userpics' in face:
                return HttpResponseNotFound('no such face', content_type='text/plain')

            face = face.rsplit('/', 1)[-1].split('-', 1)[0]
        else:
            face = face.face

        cache.set(cache_key, face)

    url = 'http://a0.typepad.com/%s-%s' % (face, spec)
    return HttpResponseRedirect(url)


def facegrid(request):
    with typepad.client.batch_request():
        events1 = request.group.events
        events2 = request.group.events.filter(start_index=51, max_results=50)
        events3 = request.group.events.filter(start_index=101, max_results=50)

    photos = []
    for events in (events1, events2, events3):
        for event in events:
            if event.object is not None:
                if type(event.object) is Photo:
                    photos.append(event.object)

    return TemplateResponse(request, 'makeaface/grid.html', {
        'photos': photos,
    })


def faq(request):
    return TemplateResponse(request, 'makeaface/faq.html', {
    })
