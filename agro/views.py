import datetime

from django.http import *
from django.shortcuts import *
from django.template import loader, Context, RequestContext

from agro.models import Entry

def entry_detail(request, entry_id=0, template_name="entry_detail.html"):
    entry = get_object_or_404(entry_id)

    assert False

    c = dict(
        entry = entry,
        object = entry.object
    )
    return render_to_response(template_name, c, context_instance=RequestContext(request))


def entry_list(request, reverse=False, for_type=None, exclude_type=None, for_user=None, day=None, month=None, year=None, add_to_context=None, template_name="entry_list.html"):
    # get all entries first, then we will pair it down
    entries = Entry.objects.all()

    if for_user: entries = entries.filter(owner_user__username__icontains=for_user)
    if for_type: entries = entries.filter(source_type__icontains=for_type)

    if year: entries = entries.filter(timestamp__year=year)
    if month: entries = entries.filter(timestamp__month=month)
    if day: entries = entries.filter(timestamp__day=day)

    if reverse: entries = entries.reverse()
    if exclude_type: entries = entries.exclude(source_type__icontains=exclude_type)

    # our context dictionary, can be built up by other functions that "subclass" this one
    c = dict(
        type = for_type,
        entries = entries,
    )
    if add_to_context:
        c = dict(c, **add_to_context)

    return render_to_response(template_name, c, context_instance=RequestContext(request))

def today(request, **kwargs):
    y, m, d = datetime.date.today().strftime("%Y/%m/%d").lower().split("/")
    return entry_list(request, reverse=True, day=d, month=m, year=y, add_to_context={'date': '%s/%s/%s' % (m,d,y)}, **kwargs)

def for_type(request, for_type, **kwargs):
    return entry_list(request, for_type=for_type, add_to_context={'type':for_type,}, **kwargs)
