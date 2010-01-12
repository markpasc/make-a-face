from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'makeaface.views.Home', name='home'),
    url(r'^$', 'makeaface.views.Home', name='group_events'),
)
