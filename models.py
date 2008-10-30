from django.db import models
from tagging.fields import TagField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from agro.managers import EntryManager
from agro.sources import *

class Entry(models.Model):
	content_type	= models.ForeignKey(ContentType)
	object			= GenericForeignKey()
	object_id		= models.IntegerField()
	owner_user		= models.CharField(max_length=200,)
	timestamp		= models.DateTimeField()
	tags			= TagField()
	objects			= EntryManager()

	class Meta:
		ordering = ['-timestamp']
		unique_together = [('content_type', 'object_id'),]
		app_label = "agro"
		verbose_name_plural = "entries"

	def __str__(self):
		return "%s: %s" % (self.content_type.model_class().__name__, self.id)

	def __cmp__(self, other_entry):
		return cmp(self.timestamp, other_entry.timestamp)

	def __unicode__(self):
		return "%s: %s" % (self.content_type, self.object_id)

	def get_tag_list(self):
		return self.tags.split()

import_source_modules()
