import datetime
from django.conf.urls.defaults import *
from agro.views import *
from agro.auth_views import *

urlpatterns = patterns('',
    url(r'twitter/$',                for_type,      {'for_type':'tweet',}, name="for-twitter"),
    url(r'(?P<for_type>\w{2,12})/$', for_type,      {},                    name="for-type"),
    url(r'$',                        entry_list,    {},                    name="tumblog"),
    url(r'^agro/flickr_token_gen/$', auth_flickr ,                         name="flickr-token-gen"),
)

