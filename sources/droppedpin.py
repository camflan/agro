import datetime
import imaplib
import logging
import pytz
import re
import urllib

from django.conf import settings
from django.db import models
from django.contrib import admin
from django.template import Template
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_unicode

from agro.models import Entry, GeolocatedEntryMixin
from agro.geo import reverse_geocode

log = logging.getLogger('agro.sources.droppedpin')

utc = pytz.utc
our_timezone = pytz.timezone(settings.TIME_ZONE)

DEFAULT_SUBJECT = "Dropped Pin"  # will be removed from name of location, if nothing else, replaced by city/state

DATE_PATTERN    = r'''
                    
                    Date:\s{0,5}\w{3},\s        #     find the beginning of the delivery date string, including the day of the week.
                    (\d{1,2})                   # (1) date: 1-31
                    \s                          #     space
                    (\w{3})                     # (2) month: 3 letter abbrev
                    \s                          #     space
                    (\d{2,4})                   # (3) year: 2 or 4 digit
                    \s                          #     space
                    (                           # (4) we capture the entire time as a string, might as well.
                        (\d{1,2})               # (5) hour: 0-24
                        :                       #     time separator
                        (\d{1,2})               # (6) minutes: 0-59
                        :                       #     time separator
                        (\d{1,2})               # (7) seconds: 0-59
                    )
                    \s                          #     space
                    (-)                         # (8) plus or minus from UTC/GMT
                    (\d{4})                     # (9) time offset

                  '''
SUBJECT_PATTERN = r'''
                    
                    \n                        # lessen the chance of picking up something from the body.
                    Subject:\s*               # find our line
                    ([^\r]*)                  # grab anything up to a new line
                    \r?\n                     # end of line, go home.
                        
                  '''

GMAPS_LL_PATTERN= r'''

                   https?://maps.google.com/maps\?f=q\&q=   # base URL
                   (-?[\d.]{4,10})                          # latitude (comes first in URL)
                   ,                                        # comma seperated
                   (-?[\d.]{4,10})                          # longitude (comes first in URL)
                   .*\s                                     # rest of the URL

                  '''


MONTH_TO_NUM = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12,}


#model def
class DroppedPin(Entry, GeolocatedEntryMixin):
    class Meta:
        ordering = ['timestamp',]
        app_label = "agro"

    def save(self, **kwargs):
        self.title = self.title.replace(DEFAULT_SUBJECT, "").strip()

        if self.title == '':
            self.title = "%s" % address

        super(DroppedPin, self).save(**kwargs)

    def __unicode__(self):
        if self.has_location_information:
            return u"(%f, %f) in %s" % (self.latitude, self.longitude, self.state)

    @property
    def format_template(self):
        return Template("<div class='entry location'><img src='{{ curr_object.static_map }}' /><p>{{ curr_object.latitude }}, {{ curr_object.longitude }}</p></div>")


class DroppedPinAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'city', 'state', 'latitude', 'longitude',)
    date_hierarchy = 'timestamp'


def retrieve(force, **args):
    """ we handle the email box here """

    username, password = args['account']
    host, mailbox, delete_on_import = args['advanced']
    
    if mailbox.lower() == 'default' or mailbox.lower() == 'inbox':
        mailbox = 'INBOX'

    last_update = datetime.datetime.fromtimestamp(0)
    if force: 
        log.info("Forcing update of all available emails from %s on %s" % (mailbox, host))
    else:
        try:
            last_update = DroppedPin.objects.filter(owner_user=username).order_by('timestamp')[0]
        except Exception, e:
            log.debug("%s", e)

    log.debug('last update: %s', last_update)

    M = imaplib.IMAP4(host)
    status, message = M.login(username, password)
    if not status == 'OK':
        log.error("Unable to login to %s using %s" % (host, username))
    status, count = M.select(mailbox)   # count is number of emails in the mailbox
    if not status == 'OK':
        log.error("Unable to open %s on %s for %s" % (mailbox, host, username))

    if count[0] == '0':
        log.info("no emails to process, exiting.")
        logout_and_close_mailbox(M)
        return

    typ, data = M.search(None, 'ALL')

    for num in data[0].split():
        handle_email(M, num, username)
#        if delete_on_import:
#            M.store(num, '+FLAGS', '\\Deleted')

    logout_and_close_mailbox(M)

def handle_email(M, num, user):
    typ, data = M.fetch(num, '(RFC822)')
    message, flags = data[0][1], data[1]

    subject_compiled_pattern = re.compile(SUBJECT_PATTERN, re.VERBOSE)
    lat_long_compiled_pattern = re.compile(GMAPS_LL_PATTERN, re.VERBOSE)
    date_compiled_pattern = re.compile(DATE_PATTERN, re.VERBOSE)

    subject = re.search(subject_compiled_pattern, message)
    delivery_date = re.search(date_compiled_pattern, message)
    lat_long = re.search(lat_long_compiled_pattern, message)

    subject = subject.group(1).strip()
    lat,lng = float(lat_long.group(1)), float(lat_long.group(2))

    address, zip, city, state, country = reverse_geocode(lat, lng)

    log.info("working with location: %s (%f, %f)" % (subject, lat, lng))

    M.noop()  # keep connection alive

    pin_date      = int(delivery_date.group(1))
    pin_month     = MONTH_TO_NUM[delivery_date.group(2).lower()]
    pin_year      = int(delivery_date.group(3))
    pin_hour      = int(delivery_date.group(5))
    pin_minute    = int(delivery_date.group(6))
    pin_seconds   = int(delivery_date.group(7))
    pin_plusminus = delivery_date.group(8)
    pin_tzoffset  = delivery_date.group(9)

    if pin_plusminus == '-':
        pin_hour = pin_hour + int(pin_tzoffset[0:2])
    else:
        pin_hour = pin_hour - int(pin_tzoffset[0:2])

    delivery_datetime = datetime.datetime(pin_year, \
                                          pin_month, \
                                          pin_date,\
                                          pin_hour,\
                                          pin_minute,\
                                          pin_seconds,\
                                          0,\
                                          tzinfo=utc)
    our_delivery_datetime = delivery_datetime.astimezone(our_timezone)

    dpobj, created = DroppedPin.objects.get_or_create(
        title = subject,
        owner_user = smart_unicode(user),
        timestamp = our_delivery_datetime,
        longitude = lng,
        latitude = lat,
        address = address,
        zip = zip,
        city = city,
        state = state,
        country = country,
        source_type = "droppedpin"
    )

def logout_and_close_mailbox(M):
    M.expunge()
    M.close()
    M.logout()

admin.site.register(DroppedPin, DroppedPinAdmin)
