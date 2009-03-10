from django.db import models

from agro.managers import EntryManager
from agro.sources import import_source_modules
from tagging.fields import TagField, Tag

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

import_source_modules()
