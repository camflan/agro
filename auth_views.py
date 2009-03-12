from django import forms
from agro.sources.flickr import FClient
from django.template import loader, Context, RequestContext
from django.shortcuts import *
from django.http import *
import urllib, md5
import logging

log = logging.getLogger('im.auth_flickr')

def auth_flickr(request):
    from agro.sources import utils
    api, secret, url = 'e22dd4a81125531e047036ed1ab2a9e7', '72a484d250375bdf', ''
    token = ''
    user_name, user_id = '', ''

    frob = request.GET.get('frob', '')

    if frob:
        api_sig = md5.new('%sapi_key%sfrob%smethodflickr.auth.getToken' % (secret, api, frob)).hexdigest()
        params = urllib.urlencode({'api_key':api, 'frob':frob, 'method':'flickr.auth.getToken', 'api_sig':api_sig})
        res = utils.get_remote_data("http://api.flickr.com/services/rest/?" + params)

        if res.get("stat", "") == "fail":
            log.error("flickr retrieve failed.")
            log.error("%s" % res.get("stat"))
            return False

        #token = res.get('auth')
        auth_res = res.getchildren()[0]
        token = auth_res.find('token').text
        user = auth_res.find('user')
        user_name = user.get('username')
        user_id = user.get('nsid')

    else:
        if request.method == 'POST':
            perms = 'read'
            api_sig = md5.new('%sapi_key%sperms%s' % (secret, api, perms)).hexdigest()
            params = urllib.urlencode({'api_key':api, 'perms':perms, 'api_sig':api_sig})
            return HttpResponseRedirect('http://flickr.com/services/auth/?%s' % params)
        else:
            pass

    return render_to_response('flickr_auth.html', {'api':api, 'secret':secret, 'user_name':user_name, 'user_id':user_id, 'token':token,}, context_instance=RequestContext(request))
