from django.db import models

from agro.managers import EntryManager
from agro.sources import import_source_modules
from tagging.fields import TagField, Tag

NEARBY_ADDRESS_GEONAMES_URL = "http://ws.geonames.org/findNearestAddressJSON?"

class Entry(models.Model):
    title           = models.CharField(max_length=200, help_text="Main text, or Title, of your entry.", blank=True)
    timestamp       = models.DateTimeField(help_text="Timestamp for your entry. This is how we pull items out of the DB.", blank=True)
    description     = models.TextField(help_text="Description, or subtext, of your entry.", blank=True)
    owner_user      = models.CharField(max_length=200, help_text="Here we store the username used for the webservice, for this entry.", blank=True)
    url             = models.URLField(verify_exists=False, help_text="URL back to the original item.", blank=True)
    source_type     = models.CharField(max_length=200, help_text="Type of entry.", blank=True)

    objects         = EntryManager()
    tags            = TagField()

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
        app_label = "agro"
        verbose_name_plural = "entries"
        unique_together = [('title', 'timestamp', 'source_type'),]

    def __unicode__(self):
        return u"%s" % self.title

    def __cmp__(self, other_entry):
        return cmp(self.timestamp, other_entry.timestamp)

    @property
    def object(self):
        return getattr(self, self.source_type)

    def _get_tags(self):
        return Tag.objects.get_for_object(self)
    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)
    tags = property(_get_tags, _set_tags)


class GeolocatedEntryMixin(models.Model):
    """
    This is for anything we want to attach 
    location information to.
    
    """

    longitude = models.FloatField()
    latitude = models.FloatField()

    country = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    zip = models.IntegerField(null=True, blank=True)
    neighborhood = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def has_location_information(self):
        if self.state and self.city:
            return True
        return False

    @property
    def coordinates(self):
        return u"%f,%f" % (self.latitude, self.longitude)

    def static_map(self, letter=None, size="512x512", type=None, color='blue'):
        kwargs = {}

        try:
            maps_api = settings.GMAPS_API_KEY
        except Exception, e:
            log.error("No google maps api defined (settings.GMAPS_API_KEY).")
            return False

        if not letter:
            letter = self.nickname[0].lower()
            color = color + letter

        kwargs['key'] = maps_api
        kwargs['center'] = self.coordinates
        kwargs['size'] = size
        if type:
            kwargs['maptype'] = type
        kwargs['markers'] = "%s,%s,%s" % (self.latitude, self.longitude, color)

        return BASE_STATIC_MAP_URL + urllib.urlencode(kwargs)

import_source_modules()
