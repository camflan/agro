from agro.models import Entry
from agro.sources import utils

def migration_script(from_mdl, to_mdl, map_dict):
    old_objs = from_mdl.objects.filter(source='jellyroll.providers.twitter')
    print len(old_objs)
    for oobj in old_objs:
        print oobj.id
        nobj = to_mdl()

        for f,t in map_dict['columns']:
            try:
                setattr(nobj, t, getattr(oobj, f))
            except AttributeError:
                setattr(nobj, t, getattr(oobj.object, f))
            except:
                pass
        for f,t in map_dict['constants']:
            setattr(nobj, t, f)

        nobj.save()
        entry = Entry.objects.create_or_update_entry(instance=nobj, tags=_tweet_to_tags(nobj.text))


def _tweet_to_tags(text):
    tags = []
    for x in text.strip('\'\".,!#$%^&?|<>[]{}').lower().split():
        if x not in utils.STOPWORDS:
            tags.append(x)
    return " ".join(tags)

mapping =   {
                'columns':
                            (
                                ('quote', 'text',),
                                ('speaker', 'tweeter',),
                                ('source_id', 'tweet_id'),
                                ('timestamp', 'timestamp'),
                            ), 
                'constants':
                            (
                                ('', 'source'),
                            ),
            }
