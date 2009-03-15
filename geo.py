import logging
import urllib

from agro.sources import utils

NEARBY_ADDRESS_GEONAMES_URL = "http://ws.geonames.org/findNearestAddressJSON?"
log = logging.getLogger('agro.geo')

def reverse_geocode(lat, lng):
    """
    Geonames response
    -----------------
            {'address': 
                {'distance': '0.03', 
                'countryCode': 'US', 
                'placename': 'Lawrence', 
                'lat': '38.946397849397954', 
                'street': 'W 21st St', 
                'streetNumber': '1446', 
                'postalcode': '66046', 
                'lng': '-95.25217028671905', 
                'adminName2': 'Douglas', 
                'adminCode1': 'KS', 
                'adminCode2': '045', 
                'adminName1': 'Kansas'
                }
            }
    -----------------

    """
    kwargs = {'lat':lat, 'lng':lng}
    
    res = utils.get_remote_data(NEARBY_ADDRESS_GEONAMES_URL + urllib.urlencode(kwargs), rformat='json')

    if not res:
        log.error("geonames failed.")
        return False

    try:
        address = "%s %s" % (res['address']['streetNumber'], res['address']['street'])
    except:
        address = False

    try:
        zip = res['address']['postalcode']
    except:
        zip = False

    try:
        city = res['address']['placename']
    except:
        city = False

    try:
        state = res['address']['adminCode1']
    except:
        state = False

    try:
        country = res['address']['countryCode']
    except:
        country = False
    return address, zip, city, state, country

