from django.db import models
from django.contrib import admin
from django.template import Template

from agro.models import Entry


#model def
class DroppedPin(Entry):
    nickname = models.CharField(max_length=200,)
    slug = models.CharField(max_length=200,)

    longitude = models.FloatField()
    latitude = models.FloatField()

    created = models.DateTimeField(unique=True,)
    imported = models.DateTimeField(auto_now_add=True,)

    country = models.CharField(max_length=200,)
    state = models.CharField(max_length=200,)
    city = models.CharField(max_length=200,)
    zip = models.IntegerField()
    neighborhood = models.CharField(max_length=200,)
    address = models.CharField(max_length=200,)

    class Meta:
        ordering = ['created',]
        app_label = "agro"

    def __unicode__(self):
        if self.has_location_information:
            return u"(%f, %f) in %s" % (self.latitude, self.longitude, self.state)

    @property
    def format_template(self):
        return Template("<div class='entry location'><p>{{ curr_object.latitude }}, {{ curr_object.longitude }}</p></div>")

    @property
    def has_location_information(self):
        if self.state and self.city:
            return True
        return False


class DroppedPinAdmin(admin.modelAdmin):
    list_display = ('nickname', 'city', 'state', 'latitude', 'longitude',)
    date_hierarchy = 'created'


def retrieve(force, **args):
    """ we handle the email box here """

    username, password = args['account']
    host, mailbox, delete_on_import = args['advanced']
    
    if mailbox.lower() == 'default' or mailbox.lower() == 'inbox':
        mailbox = 'INBOX'

    last_update = datetime.datetime.fromtimestamp(0)
    if force: 
        log.info("Forcing update of all available emails from %s on %s" % (mailbox, server))
    else:
        try:
            last_update = DroppedPin.objects.filter(owner_user=username).order_by('timestamp')[0]
        except Exception, e:
            log.debug("%s", e)

    log.debug('last update: %s', last_update)

    M = imaplib.IMAP4(server)
    M.login(username, password)
    count = M.select(mailbox)   #count is number of emails in the mailbox

    typ, data = M.search(None, 'ALL')

    for num in data[0].split():
        handle_email(M, num)

    logout_and_close_mailbox(M)

def handle_email(M, num):
    typ, data = M.fetch(num, '(RFC822)')
    print 'Message %s\n\n%s\n\n' % (num, data)

def logout_and_close_mailbox(M):
    M.close()
    M.logout()
