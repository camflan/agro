from django.db import models
from django.contrib import admin
from agro.sources import utils
from agro.models import Entry
from django.template import Template
from tagging.fields import TagField
import datetime
import logging

log = logging.getLogger('agro.sources.lastfm')

# model definition
class Song(Entry):
    artist      = models.CharField(max_length=200,)
    album       = models.CharField(max_length=200,)

    song_mbid   = models.CharField(max_length=200,)
    artist_mbid = models.CharField(max_length=200,)
    album_mbid  = models.CharField(max_length=200,)

    streamable  = models.BooleanField(default=False,)
    timestamp   = models.DateTimeField()

    small_image = models.URLField(verify_exists=False,)
    med_image   = models.URLField(verify_exists=False,)
    large_image = models.URLField(verify_exists=False,)

    class Meta:
        app_label = "agro"
        ordering = ['-timestamp']

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
def retrieve(force, **args):
    username        = args['account']
    api_key,secret  = args['api_key']
    limit = "1000"
    url             = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=%s" % (username, api_key, limit)
    song_resp       = utils.get_remote_data(url)

    last_update = datetime.datetime.fromtimestamp(0)
    if force:
        log.info("Forcing update of all available songs.")
    else:
        try:
            last_update = Song.objects.filter(username=username).order_by('-timestamp')[0].timestamp
        except Exception, e:
            log.debug("%s", e)

    if not song_resp.get('status') == 'ok':
        log.error('Last.fm responded with an error: %s', song_resp.get('status'))
        return

    lastfm_user = song_resp[0].get('user')
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

    artist = song.find('artist')
    album  = song.find('album')
    images = song.findall('image')
    imageset = {}

    for image in images:
        imageset[image.get('size')] = image.text

    song, created = Song.objects.get_or_create(
        title       = song.find('name').text or '',
        artist      = artist.text or '',
        timestamp   = dt,
        owner_user  = user_name,
        defaults=   {
            album: album.text or '',
            song_mbid: song.find('mbid').text or '',
            artist_mbid: artist.get('mbid') or '',
            album_mbid: album.get('mbid') or '',
            url: song.find('url').text or '',
            streamable: song.find('streamable').text or 0,
            small_image: imageset['small'] or '',
            med_image: imageset['medium'] or '',
            large_image: imageset['large'] or '',
        }
    )

admin.site.register(Song, SongAdmin)
