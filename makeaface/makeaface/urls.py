from django.conf.urls.defaults import *

from motion.feeds import PublicEventsFeed


urlpatterns = patterns('',
    url(r'^$', 'makeaface.views.home', name='home'),
    url(r'^$', 'makeaface.views.home', name='group_events'),

    url(r'^entry/(?P<id>\w+)$', 'django.views.generic.simple.redirect_to',
        {'url': r'/photo/%(id)s'}),
    url(r'^photo/(?P<xid>\w+)$', 'makeaface.views.photo', name='photo'),

    url(r'^upload$', 'makeaface.views.upload_photo', name='upload_photo'),
    url(r'^favorite$', 'makeaface.views.favorite', name='favorite'),
    url(r'^flag$', 'makeaface.views.flag', name='flag'),
    url(r'^asset_meta$', 'motion.ajax.asset_meta', name='asset_meta'),

    url(r'^grid$', 'makeaface.views.facegrid', name='facegrid'),
)

urlpatterns += patterns('',
    url(r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed',
        {'feed_dict': {'faces': PublicEventsFeed}}, name='feeds'),
)
