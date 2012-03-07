from django import template
from agro.models import Entry
from django.template.loader import render_to_string
from agro.sources import import_source_modules

register = template.Library()

@register.tag(name="get_latest")
def get_latest(parser, token):
    """ 
    Return a list of entries to your template as a context variable.

    Arguments::

        Limit:  This is the maximum number of entries to return.

        Type:   This can be a single type, either quoted or not, or a quoted space-delimited list of types. 
            ** USE 'entries' to return all entries **

        User:   This can be a single user, either quoted or not, or a quoted space-delimited list of usernames. 
            ** DEFAULTS to all users **

        Var:    This is the varible you want to use in your template, all found entires are returned to this variable. 
            ** DEFAULTS to 'entry_list' **

    Syntax::

        {% get_latest <limit> <type> [[by <user>] as <var>] %}

    Usage::

        {% get_latest 5 entries as entries %}   OR
        {% get_latest 10 photo as entries %}    OR
        {% get_latest 10 "photo" as entries %}  OR
        {% get_latest 10 "photo bookmark" as marks_and_photos %}    OR
        {% get_latest 100 entries by "camflan" as camflans_stuff %} OR
        {% get_latest 52 "tweet bookmark" by "camflan drhorrible" as tweets_and_marks %}

    """

    bits = token.split_contents()
    kwargs = {'limit':bits[1], 'entry_type':bits[2], 'varname':'entry_list',}

    bits = iter(bits[2:])
    while True:
        try:
            bit = bits.next()
        except StopIteration:
            break
        except:
            continue

        if bit == "by":
            kwargs['username'] = bits.next()
        elif bit == "as":
            kwargs['varname'] = bits.next()
        else:
            pass

    return LatestEntriesNode(**kwargs)

class LatestEntriesNode(template.Node):
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            if not v == v.strip('\'\"'):
                kwargs[k] = v.strip('\'\"').split()

        self.entry_type = kwargs['entry_type']
        self.limit = int(kwargs['limit'])
        self.varname = kwargs['varname']
        try:
            self.username = kwargs['username']
        except KeyError:
            self.username = None

    def render(self, context):
        try:
            if self.username:
                context[self.varname] = Entry.objects.get_of_type_for_user(self.entry_type, self.username).select_related()[:self.limit]
            else:
                context[self.varname] = Entry.objects.get_of_type(self.entry_type).select_related()[:self.limit]

            if self.limit == 1:
                context[self.varname] = context[self.varname][0]
        except:
            pass
        return ''


@register.tag(name="format")
def format_entry(parser, token):
    """ 
    Used to format an entry for pretty output to the web. 
    
    It will default to using the builtin format_template of the entry's object. 
    Can specify a template or a directory of templates. When specifying a directory, 
    it will look for a template named the same as the name of the object. 

    Arguments::

        Template: This is can be a specific template file, or a directory. If it's a
              directory, then files in that directory must be named the same as the model.
              example: tweet.html, photo.html, bookmark.html

    Syntax::

    {% format entry [using <template> [dir]] %}

    Usage::

    {% format entry %}  OR
    {% format entry using "flickr.html" %}  OR
    {% format entry using "entry_formats" dir %} OR
    {% format entry using "entry_formats/mobile" dir %}

    """
    bits = token.split_contents()
    if len(bits) in [4,5,]:
        if bits[2] == 'using':
            if len(bits) == 5:
                if bits[4] == 'dir':
                    return FormatNode(bits[1], bits[3], True)
                elif bits[4]:
                    raise template.TemplateSyntaxError("Unknown argument: %s", bits[2])
            return FormatNode(bits[1], bits[3])
        else:
            raise template.TemplateSyntaxError("Unknown argument: %s", bits[2])
    if len(bits) == 2:
        return FormatNode(bits[1])

class FormatNode(template.Node):
    def __init__(self, entry, custom_template=None, using_dir=False):
        self.entry = template.Variable(entry)
        self.custom_template = custom_template
        self.using_dir = using_dir

    def render(self, context):
        try:
            entry = self.entry.resolve(context)
            object = entry.object
            context.update({
                                "curr_entry":entry, 
                                "curr_object": object,
                            })

            if not self.custom_template:
                return object.format_template.render(context)
            elif self.custom_template:
                self.custom_template = self.custom_template.strip('\"\'')
                if self.using_dir:
                    return render_to_string('%s/%s.html' % (self.custom_template, type(object).__name__.lower()), context)
                return render_to_string(self.custom_template, context)
            else:
                return ''
        except:
            return ''
