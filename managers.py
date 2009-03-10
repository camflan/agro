from django.db import models

class EntryManager(models.Manager):
    def get_of_type_for_user(self, type_str_or_list, username_or_list):
        obj_list = self.get_of_type(type_str_or_list)
        if obj_list:
            return self.get_for_user(username_or_list, obj_list)
        return obj_list

    def get_of_type(self, type_str_or_list, obj_list=None):
        if not obj_list:
            obj_list = super(EntryManager, self).all()
        if isinstance(type_str_or_list, (list, tuple,)):
            return obj_list.filter(source_type__in=type_str_or_list)
        if type_str_or_list == 'entries':
            return obj_list
        return obj_list.filter(source_type=type_str_or_list)

    def get_for_user(self, username_or_list, obj_list=None):
        if not obj_list:
            obj_list = super(EntryManager, self).all()
        if isinstance(username_or_list, list):
            return obj_list.filter(owner_user__in=username_or_list)
        elif isinstance(username_or_list, (str, unicode)):
            return obj_list.filter(owner_user=username_or_list)
        return False
