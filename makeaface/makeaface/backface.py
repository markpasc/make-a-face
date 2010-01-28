from collections import defaultdict
import logging

from django.http import HttpResponse
from typepad import TypePadObject
from typepadapp.models.users import User

from makeaface.models import Favoriteface, Lastface
from makeaface.views import oops


log = logging.getLogger(__name__)


def all_items(source):
    """Generates all items of a TypePad API List, traversing through subsequent
    pages as necessary."""
    i = 1
    log.debug("Should be %d results", source.total_results)
    while True:
        page = source.filter(start_index=i, max_results=50)
        log.debug("Yay page starting at %d is %r", i, page._location)
        i += 50
        if len(page):
            log.debug("Yay %d items in page (first is %r)", len(page), page[0])
            for item in page:
                yield item
        else:
            log.debug("Whee returning since there were no items in page?")
            return


@oops
def backface(request):
    TypePadObject.batch_requests = False

    faces = list(all_items(request.group.events))

    # Get all the faces.
    author_faces = defaultdict(list)
    for newface in faces:
        if 'tag:api.typepad.com,2009:NewAsset' not in newface.verbs:
            continue
        face = newface.object
        if face is None:
            continue
        au = face.author.xid
        author_faces[au].append(face)

    # Put each author's faces in published order (though they're probably already in that order).
    for author, au_faces in author_faces.items():
        author_faces[author] = sorted(au_faces, key=lambda x: x.published)

    for author, au_faces in author_faces.items():
        # Missing Lastface? Add one in.
        try:
            Lastface.objects.get(owner=author)
        except Lastface.DoesNotExist:
            # OHNOES MISSING LASTFACE
            log.info("Filling in %r's Lastface", au_faces[-1].author.display_name)
            au_face = au_faces[-1]
            Lastface(owner=author, face=au_face.xid,
                created=au_face.published).save()

        # Go through the author's favorites, filling in any missing Favoritefaces.
        events = User.get_by_url_id(author).events.filter(by_group=request.group.xid)
        for fav in all_items(events):
            if 'tag:api.typepad.com,2009:AddedFavorite' not in fav.verbs:
                continue

            # Is there a Favoriteface for that?
            favoriter = fav.actor.xid
            try:
                Favoriteface.objects.get(favoriter=favoriter,
                    favorited=fav.object.xid)
            except Favoriteface.DoesNotExist:
                # NO FAVFACE OHNOES
                log.info("Filling in %r's Favoriteface for %r", au_faces[-1].author.display_name, fav.object.xid)
                when = fav.published
                au_faces_before = [x for x in au_faces if x.published < when]
                if not au_faces_before:
                    continue
                au_face = au_faces_before[-1]

                favface = Favoriteface(favoriter=favoriter, favorited=fav.object.xid)
                favface.lastface = au_face.xid
                favface.created = fav.published
                favface.save()

    return HttpResponse('OK', content_type='text/plain')
