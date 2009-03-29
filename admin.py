from agro.models import *
from agro.sources import *
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'url',)
    list_filter = ('source_type',)
    date_hierarchy = 'timestamp'

#admin.site.register(Entry, EntryAdmin)
admin.site.register(Entry)

import_source_modules(class_name='Admin')
