from django.conf import settings
import logging

log = logging.getLogger('agro.sources')

tree_modules_to_try =   [ "xml.etree.cElementTree", "elementtree.ElementTree", "cElementTree", ]
element_tree = None

for tree in tree_modules_to_try:
    try:
        try:
            element_tree = __import__('%s' % tree, {}, {}, [''], -1)
        except:
            element_tree = __import__('%s' % tree, {}, {}, [''])
        break
    except ImportError, e:
        continue
    except Exception, e:
        log.error("%s" % e)
        raise

if element_tree is None:
    raise ImportError("No ElementTree found.")
log.debug("Using specified etree module: %s" % element_tree)

def import_source_modules(source_list=settings.AGRO_SETTINGS['source_list'], class_name=''):
    sources = []
    for source in source_list:
        try:
            log.debug('trying to load %s' % source)
            try:
                s = __import__("agro.sources.%s" % source, {}, {}, ['%s%s' % (source, class_name)], -1)
            except:
                s = __import__("agro.sources.%s" % source, {}, {}, ['%s%s' % (source, class_name)])
            if s:
                sources.append(s)
        except Exception, e:
            log.error('unable to load %s: %s', source, e)
    return sources
