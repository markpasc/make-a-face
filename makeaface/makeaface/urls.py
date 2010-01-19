from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'makeaface.views.home', name='home'),
    url(r'^$', 'makeaface.views.home', name='group_events'),
    url(r'^entry/(?P<id>\w+)$', 'django.views.generic.simple.redirect_to',
        {'url': r'/#%(id)s'}),
    url(r'^upload$', 'makeaface.views.upload_photo', name='upload_photo'),
    url(r'^favorite$', 'makeaface.views.favorite', name='favorite'),
    url(r'^flag$', 'makeaface.views.flag', name='flag'),
)
