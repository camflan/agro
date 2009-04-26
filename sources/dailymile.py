from django.db import models
from django.contrib import admin
from agro.sources import utils
from agro.models import Entry
from django.template import Template
from tagging.fields import TagField
import datetime
import logging
import re

from agro.sources.baserss import BaseRSS
from agro.sources.baserss import retrieve as super_retrieve

log = logging.getLogger('agro.sources.dailymile')

# model definition
class DailyMile(BaseRSS):
    distance = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)
    felt = models.CharField(max_length=200)

    @property
    def format_template(self):
        return Template("<div class='entry dm'><a href='{{ curr_object.url }}'>{{ curr_object.title }}</a></div>")

# retrieve function
def retrieve(force, **args):
    more_args = {
        'tags': ['distance', 'duration', 'felt'],
        'model': DailyMile,
        'url': 'http://www.dailymile.com/people/%s/entries.atom' % args['account'],
        'feedtype': 'atom',
        'processors': {'title': title_processor,},
    }
    args = dict(args, **more_args)
    super_retrieve(force, **args) 
    log.debug("done with retrieve")


def title_processor(s):
    s = re.sub('(.*)(\sposted a \w+\sworkout)', 'I\g<2>.', s)
    return s

admin.site.register(DailyMile)
