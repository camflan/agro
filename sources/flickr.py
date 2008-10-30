from django.db import models
from django.contrib import admin
from agro.sources import utils
from agro.models import Entry
from tagging.fields import TagField
from django.utils.encoding import smart_unicode
from django.template import Template
import datetime
import urllib
import logging
import md5
import re

log = logging.getLogger('agro.sources.flickr')

# model definition
class Photo(models.Model):
    photo_id    = models.CharField(max_length=200,)
    server      = models.IntegerField(null=True,)
    secret      = models.CharField(max_length=200,null=True,)

    original_secret = models.CharField(max_length=200,null=True,)
    original_format = models.CharField(max_length=4,null=True,)

    photog      = models.CharField(max_length=200, blank=True, null=True, )
    title       = models.CharField(max_length=200,)
    description = models.TextField(blank=True, null=True,)
    num_comments= models.IntegerField(blank=True, null=True,)

    tags        = TagField()

    taken_at    = models.DateTimeField(null=True,)
    uploaded_at = models.DateTimeField(null=True,)

    exif        = models.TextField(blank=True, null=True, )

    class Meta:
        ordering = ['-uploaded_at']
        unique_together = [('photo_id', 'server'),]
        app_label = "agro"

    def __unicode__(self):
        return self.title

    @property
    def owner_user(self):
        return self.photog
    @property
    def url(self):
        return "http://www.flickr.com/photos/%s/%s" % (self.photog, self.photo_id)

    @property
    def format_template(self):
        return Template(
                "<div class = 'entry photo'><a href='{{ curr_object.url }}'><img src='{{ curr_object.square }}' /> {{ curr_object.title }}</a></div>"
        )
    
    @property
    def timestamp(self, sort_by="uploaded"):
        if not sort_by == "uploaded":
            return self.taken_at
        return self.uploaded_at

    # image urls
    @property
    def image(self):
        """ this is a 500px (longest side) image """
        return self._build_image_url()
    @property
    def thumbnail(self):
        """ this is a 100px (longest side) image """
        return self._build_image_url('t')
    @property
    def square(self):
        """ this is a 75x75 image """
        return self._build_image_url('s')
    @property
    def small(self):
        """ this is a 240px (longest side) image """
        return self._build_image_url('m')
    @property
    def large(self):
        """ this is a 1024 (longest side) image """
        return self._build_image_url('b')
    @property
    def original(self):
        """ original image, gif, png, or jpg. original size as well """
        return self._build_image_url('o')

    def _build_image_url(self, size=None):
        if size in list('stmb'):
            return "http://static.flickr.com/%s/%s_%s_%s.jpg" % (self.server, self.photo_id, self.secret, size)
        elif size == 'o':
            return "http://static.flickr.com/%s/%s_%s_o.%s" % (self.server, self.photo_id, self.original_secret, self.original_format)
        return "http://static.flickr.com/%s/%s_%s.jpg" % (self.server, self.photo_id, self.secret)

# admin definition
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('photo_id', 'title', 'taken_at', 'uploaded_at',)
    date_hierarchy = 'uploaded_at'

# retrieve function, this is how we handle items
def retrieve(force, **args):
    """ this is how we will handle photos """

    username, user_id = args['account']

    flickr = FClient(args['api_key'])

    last_update = datetime.datetime.fromtimestamp(0)
    if force:
        log.info("Forcing update of all available photos")
    else:
        try:
            last_update = Photo.objects.filter(photog=username).order_by('-uploaded_at')[0].uploaded_at
        except Exception, e:
            log.debug("%s", e)

    log.debug('last update: %s', last_update)
    page = 1

    while True:
        res = flickr.exe_method('people.getPublicPhotos', user_id=user_id, extras="date_taken,last_update,tags", per_page='500', page=page)
        if res is False:
            log.error('error')
            break

        res = res['photos']
        for photo in res['photo']:
            photo_up_time = datetime.datetime.fromtimestamp(float(photo['lastupdate']))
            if last_update <= photo_up_time:
                log.debug('current photo upload time: %s', photo_up_time)
                _handle_photo(flickr, photo, username)
            else:
                break
        page += 1

        if page > res['pages']:
            log.info('no more photos')
            break

class FClient(object):
    def __init__(self, api_key):
        if isinstance(api_key, (tuple, list)):
            self.api_key, self.secret, self.token = api_key
            self.signed = True
        else:
            self.api_key =  api_key
            self.signed = False

        self.method = 'flickr'
        self.format = 'json'
        self.nojsoncallback = '1'

        log.debug('flickrclient created.')

    def exe_method(self, method, **kwargs):
        kwargs['method']    = '%s.%s' % (self.method,method)
        kwargs['api_key']   = self.api_key
        kwargs['format']    = self.format
        kwargs['nojsoncallback']= self.nojsoncallback

        url = "http://api.flickr.com/services/rest/?"
        
        for k,v in kwargs.iteritems():
            kwargs[k] = v

        if self.signed:
            kwargs['auth_token'] = self.token
            params = self.encode_and_sign(**kwargs)
            res = utils.get_remote_data(url + params, rformat='json')
        else:
            res = utils.get_remote_data(url + urllib.urlencode(kwargs), rformat='json')

        if res.get("stat", "") == "fail":
            log.error("flickr retrieve failed.")
            log.error("%s" % res.get("stat"))
            return False

        return res

    def sign(self, dictionary):
        data = [self.secret]
        for key in sorted(dictionary.keys()):
            data.append(key)
            datum = dictionary[key]
            if isinstance(datum, unicode):
                raise IllegalArgumentException("No Unicode allowed, "
                        "argument %s (%r) should have been UTF-8 by now"
                        % (key, datum))
            data.append(datum)
        
        md5_hash = md5.new()
        md5_hash.update(''.join(data))
        return md5_hash.hexdigest()

    def encode_and_sign(self, **kwargs):
        '''URL encodes the data in the dictionary, and signs it using the
        given secret, if a secret was given.
        '''
        
        dictionary = make_utf8(kwargs)
        if self.secret:
            dictionary['api_sig'] = self.sign(dictionary)
        return urllib.urlencode(dictionary)

def _handle_photo(flickr_obj, photo, user):
    photo_id        = photo['id']
    secret          = smart_unicode(photo['secret'])

    log.info('working with photo => id: %s, secret: %s', photo_id, secret)

    info = flickr_obj.exe_method('photos.getInfo', photo_id=photo_id, secret=secret)['photo']

    photo_obj, created = Photo.objects.get_or_create(
        photo_id    = photo_id,
        photog      = smart_unicode(user),
        uploaded_at = datetime.datetime.fromtimestamp(utils.safeint(info["dates"]["posted"])),
    )

    try:
        photo_obj.secret            = secret
        photo_obj.server            = utils.safeint(smart_unicode(photo['server']))
        photo_obj.original_secret   = smart_unicode(info['originalsecret'])
        photo_obj.original_format   = smart_unicode(info['originalformat'])
        photo_obj.taken_at          = photo['datetaken']
        photo_obj.title             = smart_unicode(photo['title'])
        photo_obj.description       = smart_unicode(info['description']['_content'])
        photo_obj.num_comments      = utils.safeint(info["comments"]["_content"])
        photo_obj.tags              = smart_unicode(photo['tags'])
        photo_obj.save()
    except Exception, e:
        log.error('%s' % e)

    #log.debug('tags: %s', photo.tags)
    entry = Entry.objects.create_or_update_entry(instance=photo_obj, tags=photo_obj.tags)

admin.site.register(Photo, PhotoAdmin)


def make_utf8(dictionary):
    '''Encodes all Unicode strings in the dictionary to UTF-8. Converts
    all other objects to regular strings.

    Returns a copy of the dictionary, doesn't touch the original.
    '''

    result = {}

    for (key, value) in dictionary.iteritems():
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        else:
            value = str(value)
        result[key] = value

    return result
