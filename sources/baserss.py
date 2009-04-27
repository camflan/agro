from django.db import models
from django.contrib import admin
from agro.sources import utils
from agro.models import Entry
from django.template import Template
from tagging.fields import TagField
import iso8601
import datetime
import logging

log = logging.getLogger('agro.sources.baserss')
dateparse = utils.parsedate
rformat = 'rss'
processors = None

# model definition
class BaseRSS(Entry):
    class Meta:
        abstract = True
        app_label = "agro"
        ordering = ['-timestamp']

    @property
    def format_template(self):
        return Template("<div class='entry rss'><a href='{{ curr_object.url }}'>{{ curr_object.title }}</a></div>")

# retrieve function
def retrieve(force, **args):
    username = args['account']

    try:
        url = args['url']
        MODEL = args['model']
        rss_tags = args['tags']
        source_type = args['source_type']

        if 'feedtype' in args.keys():
            rformat = args['feedtype']
    except Exception, e:
        raise

    if rformat == 'atom':
        dateparse = iso8601.parse_date

    if args['processors']:
        processors = args['processors']

    last_update = datetime.datetime.fromtimestamp(0)
    if force:
        log.info("Forcing update of all entries available.")
    else:
        try:
            last_update = MODEL.objects.filter(owner_user=username).order_by('-timestamp')[0].timestamp
        except Exception, e:
            log.debug('%s', e)

    e = utils.get_remote_data(url, rformat=rformat)

    if e:
        for entry in e['entries']:
            dt = dateparse(entry['published'])
            if rformat == 'atom':
                dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            if dt > last_update:
                log.info("working with entry => %s" % entry['title'])

                model_entry, created = MODEL.objects.get_or_create(
                    timestamp = dt,
                    title = entry['title'],
                    source_type = source_type,
                )

                model_entry.url=entry['link'],
                model_entry.owner_user=username,

                if rformat == 'atom':
                    model_entry.description = entry['content'][0].value

                if rss_tags:
                    for tag in rss_tags:
                        try:
                            setattr(model_entry, tag, entry[tag])
                        except Exception, e:
                            log.error("%s", e)
                            log.warn("Unable to set %s", tag)

                try:
                    for k,v in processors.iteritems():
                        try:
                            setattr(model_entry, k, v(getattr(model_entry, k)))
                        except:
                            raise
                except Exception, e:
                    log.warn("%s", e)

                try:
                    model_entry.save()
                except Exception, e:
                    log.warn("%s", e)
            else:
                log.warning("No more entries, stopping...")
                break
