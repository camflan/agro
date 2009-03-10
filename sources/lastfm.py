import datetime
import logging

from django.db import models
from django.db import transaction
from django.contrib import admin
from django.template import Template
from django.utils.encoding import smart_unicode

from agro.sources import utils
from agro.models import Entry

from tagging.fields import TagField

log = logging.getLogger('agro.sources.lastfm')

# model definition
class Song(Entry):
    artist      = models.CharField(max_length=200, blank=True, null=True)
    album       = models.CharField(max_length=200, blank=True, null=True)
    song_mbid   = models.CharField(max_length=200, blank=True, null=True,)
    artist_mbid = models.CharField(max_length=200, blank=True, null=True,)
    album_mbid  = models.CharField(max_length=200, blank=True, null=True,)
    streamable  = models.BooleanField(default=False,)
    small_image = models.CharField(max_length=200, blank=True, null=True)
    med_image   = models.CharField(max_length=200, blank=True, null=True)
    large_image = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label = "agro"
        ordering = ['-timestamp']

    def __unicode__(self):
        return self.title

    @property
    def username(self):
        return self.owner_user
    
    @property
    def format_template(self):
        return Template("<div class='entry song'><a href='{{ curr_object.url }}'>{{ curr_object.title }}</a></div>")


# admin definition
class SongAdmin(admin.ModelAdmin):
    list_display = ('artist', 'album', 'title', 'timestamp')
    list_filter = ('streamable', 'owner_user',)
    date_hierarchy = 'timestamp'

# retrieve function
@transaction.commit_on_success
def retrieve(force, **args):
    username        = args['account']
    api_key,secret  = args['api_key']
    url             = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=%s" % (username, api_key, 1000)
    song_resp       = utils.get_remote_data(url)

    last_update = datetime.datetime.fromtimestamp(0)
    if force:
        log.info("Forcing update of all available songs.")
    else:
        try:
            last_update = Song.objects.filter(owner_user=username)[0].timestamp
        except Exception, e:
            log.debug("%s", e)

    if not song_resp.get('status') == 'ok':
        log.error('Last.fm responded with an error: %s', song_resp.get('status'))
        return

    songs = song_resp[0].getchildren()
    user_name = song_resp[0].get('user')

    if songs:
        for song in songs:
            try:
                dt = datetime.datetime.fromtimestamp(float(song.find('date').get('uts')))
            except Exception, e:
                log.error(type(song))
                log.error(song.find('date'))
                log.error(e)
                continue
            if dt > last_update:
                _handle_song(song, dt, user_name)
            else:
                log.warning("no more songs, stopping...")
                break

def _handle_song(song, dt, user_name):
    log.info("working with song => %s" % dt)

    track = song.find('name')
    artist = song.find('artist')
    album = song.find('album')

    imageset = {}
    images = song.findall('image')

    for image in images:
        imageset[image.get('size')] = image.text

    try:
        s, created = Song.objects.get_or_create(
            title = smart_unicode(track.text),
            artist = smart_unicode(artist.text), 
            timestamp = dt,
            album = smart_unicode(album.text),
            artist_mbid = smart_unicode(artist.get('mbid')),
            album_mbid = smart_unicode(album.get('mbid')),
            url = smart_unicode(song.find('url').text),
            streamable = smart_unicode(song.find('streamable').text),
            small_image = smart_unicode(imageset.get('small', '')),
            med_image = smart_unicode(imageset.get('medium', '')),
            large_image = smart_unicode(imageset.get('large', '')),
            owner_user = smart_unicode(user_name),
            source_type = "song",
        )
    except Exception, e:
        print e
        raise

admin.site.register(Song, SongAdmin)
