import datetime

from django.conf.urls.defaults import *

from agro.views import *

urlpatterns = patterns('',
    url(r'twitter/$', for_type, {'for_type':'tweet',}, name="for-twitter"),
    url(r'today/$', today, {}, name="today"),
    url(r'(?P<for_type>\w{2,12})/$', for_type, {}, name="for-type"),
    url(r'$',   entry_list, {}, name="tumblog"),
)
