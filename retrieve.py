#!/usr/bin/evn python

from django.conf import settings
from agro.sources import *
import logging
import sys
import optparse

log = logging.getLogger('agro.retrieve')

def retrieve_data_updates(opts=None, args=None):
    log.info('starting to update sources')
    sources = settings.SOURCE_LIST

    if args and len(args) > 1:
        sources = args[1:]
        for source in sources:
            if source not in settings.SOURCE_LIST:
                log.warning('%s is not a valid source, removing from update list.', source)
                sources.remove(source)

    args = {}
    force_run = False
    if hasattr(opts, 'force'):
        if opts.force == True:
            force_run = True

    for s in import_source_modules(source_list=sources, class_name='retrieve'):
        log.info('')
        log.info('trying to update %s', s.__name__)

        base_name = s.__name__[s.__name__.rfind('.')+1:]

        if base_name in settings.AGRO_API_KEYS.keys():
            args['api_key'] = settings.AGRO_API_KEYS[base_name]

        if base_name in settings.AGRO_ACCOUNTS.keys():
            account = settings.AGRO_ACCOUNTS[base_name]
        else:
            log.error('no credentials for %s', base_name)
            continue

        if isinstance(account, (tuple, list)):
            for a in account:
                args['account'] = a
                log.info('using %s account: %s', base_name, args['account'])
                s.retrieve(force_run, **args)
        else:
            args['account'] = account
            log.info('using %s account: %s', base_name, args['account'])
            s.retrieve(force_run, **args)

        log.info('done updating %s', s.__name__)
        log.info('')


def _print_sources():
    print 'your sources:'
    for s in settings.SOURCE_LIST:
        print ' -', s

if __name__ == '__main__':
    usage = "usage: %prog [options] source1 source2 sourceN"
    parser = optparse.OptionParser(usage)
    parser.add_option("-q", "--quiet",   dest="level", action="store_const", const=logging.WARN, help="Only show errors.")
    parser.add_option("-v", "--verbose", dest="level", action="store_const", const=logging.DEBUG, help="Show all information, useful for debugging.")
    parser.add_option("-f", "--force",   action="store_true", help="Forces update for all entries, even ones already processed.")
    parser.add_option("-s", "--list-sources", action="store_true", help="Display sources you have enabled.")

    opts, args = parser.parse_args(sys.argv)

    if opts:
        log.setLevel(opts.level)
        if opts.list_sources:
            _print_sources()
            sys.exit(0)

    retrieve_data_updates(opts, args)
