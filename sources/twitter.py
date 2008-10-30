from django.db import models
from django.contrib import admin
from django.utils.encoding import smart_unicode
from agro.sources import utils
from agro.models import Entry
from django.template import Template
import logging

log = logging.getLogger('agro.sources.twitter')

# model definition
class Tweet(models.Model):
    tweet_id    = models.IntegerField(null=True, blank=True, )
    text        = models.CharField(max_length=200, null=True, blank=True, )
    tweeter     = models.CharField(max_length=200, null=True, blank=True, )
    timestamp   = models.DateTimeField()
    source      = models.TextField(blank=True, null=True, )

    class Meta:
        app_label = "agro"
        ordering = ['-tweet_id',]

    def __unicode__(self):
        return u"Tweet: %s" % self.text

    @property
    def owner_user(self):
        return self.tweeter

    @property
    def url(self):
        return "http://twitter.com/%s/statuses/%s" % (self.tweeter, self.tweet_id)

    @property
    def format_template(self):
        return Template("<div class = 'entry tweet'> {{ curr_object.text }} -- said <a href='{{ curr_object.url }}'>{{ curr_object.timestamp|timesince }}</a> ago by {{ curr_object.tweeter }}. </div>")

# admin definition (newforms admin only)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('tweet_id', 'text', 'tweeter', 'timestamp',)

# retrieve function, this is how we handle items
def retrieve(force, **args):
    """ this is how we will create new items/tweets """
    # globals
    username, password = args['account'], None
    if isinstance(username, tuple):
        username, password = username

    url = "http://twitter.com/statuses/user_timeline/%s.json" % username
    last_id = 0

    if force:
        log.info("Forcing update of all tweets available.")
    else:
        try:
            last_id = Tweet.objects.filter(tweeter=username).order_by('-tweet_id')[0].tweet_id
        except Exception, e:
            log.debug('%s', e)

    log.debug("Last id processed: %s", last_id)

    if not password:
        tweets = utils.get_remote_data(url, rformat="json", username=username)
    else:
        tweets = utils.get_remote_data(url, rformat="json", username=username, password=password)

    if not tweets:
        log.warning('no tweets returned, twitter possibly overloaded.')
        return

    for t in tweets:
        if t['id'] > last_id:
            log.info("Working with %s.", t['id'])
            tweet, created = Tweet.objects.get_or_create(
                    tweet_id    = t['id'], 
                    text        = smart_unicode(t['text']), 
                    tweeter     = smart_unicode(t['user']['screen_name']), 
                    timestamp   = utils.parsedate(t['created_at']),
                    source      = smart_unicode(t['source']),
            )

            entry = Entry.objects.create_or_update_entry(instance=tweet, tags=_tweet_to_tags(tweet.text))
        else:
            log.warning("No more tweets, stopping...")
            break

def _tweet_to_tags(text):
    tags = []
    for x in text.lower().split():
        if x not in utils.STOPWORDS:
            tags.append(x.strip('`.,!#$%^&?|<>[]{}'))
    return " ".join(tags)
    

admin.site.register(Tweet, TweetAdmin)
