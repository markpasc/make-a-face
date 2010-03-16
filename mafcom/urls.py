from django.conf.urls.defaults import *
import statical


urlpatterns = patterns('',
    url(r'^', include('makeaface.urls')),
    url(r'^', include('typepadapp.urls')),
)

urlpatterns += statical.static_url_patterns(document_root='')
