from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^', include('makeaface.urls')),
    url(r'^', include('typepadapp.urls')),
    url(r'^static/(?P<path>.*)', 'reusably.serve_static_files', {'document_root': ''}, name='static'),
)
