from django.db import models
from django.contrib import admin
from django.utils.encoding import smart_unicode
from agro.sources import utils
from agro.models import Entry
from django.template import Template
import logging

log = logging.getLogger('agro.sources.twitter')

# model definition
class Tweet(Entry):
    tweet_id    = models.BigIntegerField(null=True, blank=True, help_text="This is the id assigned to each tweet by twitter." )
    source      = models.TextField(blank=True, null=True, )

    class Meta:
        ordering = ['-tweet_id',]
        app_label = "agro"

    def __repr__(self):
        return "<Tweet id:%s>" % self.tweet_id

    def __unicode__(self):
        return u"Tweet: %s" % self.text

    # Here are a couple of properties to keep this backwards-compatible.
    @property
    def tweeter(self):
        return self.owner_user

    @property
    def text(self):
        return self.title

    @property
    def format_template(self):
        return Template("<div class = 'entry tweet'> {{ curr_object.text }} -- said <a href='{{ curr_object.url }}'>{{ curr_object.timestamp|timesince }}</a> ago by {{ curr_object.tweeter }}. </div>")

# admin definition (newforms admin only)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('tweet_id', 'text', 'tweeter', 'timestamp',)

# retrieve function, this is how we handle items
def retrieve(force, **args):
    """ this is how we will create new items/tweets """
    username, password = args['account'], None
    if isinstance(username, tuple):
        username, password = username

    url = "http://twitter.com/statuses/user_timeline/%s.json" % username
    last_id = 0

    if force:
        log.info("Forcing update of all tweets available.")
    else:
        try:
            last_id = Tweet.objects.filter(owner_user=username).order_by('-tweet_id')[0].tweet_id
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

            tweet_text = smart_unicode(t['text'])
            owner_user = smart_unicode(t['user']['screen_name'])
            url = "http://twitter.com/%s/statuses/%s" % (owner_user, t['id'])

            tweet, created = Tweet.objects.get_or_create(
                    tweet_id    = t['id'], 
                    title       = tweet_text,
                    owner_user  = owner_user,
                    timestamp   = utils.parsedate(t['created_at']),
                    source      = smart_unicode(t['source']),
                    url = url,
                    source_type = "tweet"
            )
            try:
                tweet.tags = _tweet_to_tags(tweet_text)
            except Exception, e:
                print e
                pass
        else:
            log.warning("No more tweets, stopping...")
            break

def _tweet_to_tags(text):
    tags = []
    for x in text.lower().split():
        if x not in utils.STOPWORDS:
            tags.append(x.strip('`".,!#$%^&?|<>[]{}'))
    return " ".join(tags)
    

admin.site.register(Tweet, TweetAdmin)
