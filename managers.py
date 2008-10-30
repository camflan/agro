from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class EntryManager(models.Manager):
    def create_or_update_entry(self, instance, timestamp=None,tags=""):
        ct = ContentType.objects.get_for_model(instance)
        if not timestamp:
            timestamp = instance.timestamp
        entry, created = self.get_or_create(
            content_type = ct, 
            object_id = instance._get_pk_val(),
            timestamp=timestamp,
            owner_user=instance.owner_user,
        )
        entry.tags = tags
        entry.save()

        return entry, created

    def get_of_type_for_user(self, type_str_or_list, username_or_list):
        obj_list = self.get_of_type(type_str_or_list)
        if obj_list:
            return self.get_for_user(username_or_list, obj_list)
        return obj_list

    def get_of_type(self, type_str_or_list, obj_list=None):
        if not obj_list:
            obj_list = super(EntryManager, self).all()
        if isinstance(type_str_or_list, list):
            type_str_or_list = map(self._get_type, type_str_or_list)
            return obj_list.filter(content_type__in=type_str_or_list)
        elif isinstance(type_str_or_list, (str, unicode)):
            if type_str_or_list == 'entries':
                return obj_list
            item_type = self._get_type(type_str_or_list)
            if item_type:
                return obj_list.filter(content_type=item_type)

        return False

    def get_for_user(self, username_or_list, obj_list=None):
        if not obj_list:
            obj_list = super(EntryManager, self).all()
        if isinstance(username_or_list, list):
            return obj_list.filter(owner_user__in=username_or_list)
        elif isinstance(username_or_list, (str, unicode)):
            return obj_list.filter(owner_user=username_or_list)
        return False

    def get_last_update(self, content_type_str):
        type = self._get_type(content_type_str)
        if type:
            try:
                return Entry.objects.filter(content_type=type)[0]
            except:
                return False
        return False

    def _get_type(self, str):
        try:
            return ContentType.objects.get(name=str)
        except:
            return False
