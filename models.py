from django.db import models
from django.contrib.contenttypes.models import ContentType

from agro.managers import EntryManager
from agro.sources import import_source_modules
from tagging.fields import TagField, Tag

class Entry(models.Model):
    title           = models.CharField(max_length=200, help_text="Main text, or Title, of your entry.")
    timestamp       = models.DateTimeField(help_text="Timestamp for your entry. This is how we pull items out of the DB.")
    description     = models.CharField(max_length=200, help_text="Description, or subtext, of your entry.")
    owner_user      = models.CharField(max_length=200, help_text="Here we store the username used for the webservice, for this entry.")
    url             = models.URLField(verify_exists=False, help_text="URL back to the original item.")
    source_type     = models.CharField(max_length=200, help_text="Type of entry.")

    objects         = EntryManager()
    tags            = TagField()

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
        app_label = "agro"
        verbose_name_plural = "entries"
        unique_together = ('source_type', 'title', 'timestamp')

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

import_source_modules()
