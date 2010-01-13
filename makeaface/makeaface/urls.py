from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'makeaface.views.home', name='home'),
    url(r'^$', 'makeaface.views.home', name='group_events'),
    url(r'^upload$', 'makeaface.views.upload_photo', name='upload_photo'),
)
