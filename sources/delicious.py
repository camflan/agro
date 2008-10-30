from django.db import models
from django.contrib import admin
from agro.sources import utils
from agro.models import Entry
from django.template import Template
from tagging.fields import TagField
import datetime
import logging

log = logging.getLogger('agro.sources.delicious')

# model definition
class Bookmark(models.Model):
    title       = models.CharField(max_length=200,)
    timestamp   = models.DateTimeField()
    url         = models.CharField(max_length=200,)
    username    = models.CharField(max_length=200,)
    description = models.TextField(null=True, blank=True, )

    tags        = TagField()

    class Meta:
        app_label = "agro"
        ordering = ['-timestamp']

    @property
    def owner_user(self):
        return self.username
    
    @property
    def format_template(self):
        return Template("<div class='entry bookmark'><a href='{{ curr_object.url }}'>{{ curr_object.title }}</a></div>")


# admin definition
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'timestamp')
    date_hierarchy = 'timestamp'

# retrieve function
def retrieve(force, **args):
    username = args['account']
    url      = "http://feeds.delicious.com/v2/json/%s" % username
    marks = utils.get_remote_data(url, rformat='json')

    last_update = datetime.datetime.fromtimestamp(0)
    if force:
        log.info("Forcing update of all bookmarks available.")
    else:
        try:
            last_update = Bookmark.objects.filter(username=username).order_by('-timestamp')[0].timestamp
        except Exception, e:
            log.debug('%s', e)

    if marks:
        for mark in marks:
            dt = utils.parsedate(mark['dt']) 
            if dt > last_update:
                _handle_bookmark(mark, dt, username)
            else:
                log.warning("No more bookmarks, stopping...")
                break

def _handle_bookmark(mark, dt, username):
    log.info("working with bookmark => %s" % mark['d'])

    tags = ' '.join(mark['t'])

    bookmark, created = Bookmark.objects.get_or_create(
        timestamp   = dt,
        url         = mark['u'],
        title       = mark['d'],
        username    = username,
    )

    bookmark.tags        = tags
    bookmark.description = mark['n']
    bookmark.save()

    entry = Entry.objects.create_or_update_entry(instance=bookmark, tags=tags)

admin.site.register(Bookmark, BookmarkAdmin)
