from agro.models import *
from agro.sources import *
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
	list_display = ('content_type', 'object_id', 'timestamp',)
	list_filter = ("content_type", "owner_user",)

admin.site.register(Entry, EntryAdmin)

import_source_modules(class_name='Admin')
