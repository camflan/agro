import datetime
from django.conf.urls.defaults import *
from agro.views import *
from agro.auth_views import *

urlpatterns = patterns('',
    url(r'flickr_token_gen/$',       auth_flickr ,                         name="flickr-token-gen"),
    url(r'(?P<for_type>\w{2,12})/$', for_type,      {},                    name="for-type"),
    url(r'$',                        entry_list,    {},                    name="tumblog"),
)

