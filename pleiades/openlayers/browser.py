import os
from shapely.geometry import asShape
from zope.publisher.browser import BrowserPage
from zgeo.geographer.interfaces import IGeoreferenced


class PlaceOLJS(BrowserPage):

    def __call__(self):
        response = self.request.response
        geo = IGeoreferenced(self.context)
        if geo.type == 'Point':
            centroid = geo
        else:
            shape = asShape(geo)
            centroid = shape.centroid
        response.setHeader('Content-Type', 'text/javascript')
        return """
// Javascript summary of a Pleiades entity
var pleiades_oljs = %s;
        """ % dict(
                uid=self.context.UID(),
                where=dict(type=geo.type, coordinates=geo.coordinates),
                centroid=centroid.__geo_interface__['geometry']
                )


GMAPS_KEY = os.environ.get('GMAPS_KEY', '')

class GoogleAPIKey(BrowserPage):

    def __call__(self):
        return GMAPS_KEY
