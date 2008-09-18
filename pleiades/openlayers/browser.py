import os
import geojson
from shapely.geometry import asShape
from zope.publisher.browser import BrowserPage
from zope.event import notify
from zgeo.geographer.geo import ObjectGeoreferencedEvent
from zgeo.geographer.interfaces import IGeoreferenced
from pleiades.openlayers.proj import Transform, PROJ_900913


class OLSphericalMercatorJS(BrowserPage):
    """Returns coordinates projected to Spherical Mercator for use with 
    Google Maps.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.transform = Transform(PROJ_900913)

    def __call__(self):
        response = self.request.response
        geo = IGeoreferenced(self.context)
        where = self.transform(geo)
        if geo.type == 'Point':
            centroid = where
        else:
            shape = asShape(geo)
            centroid = self.transform(shape.centroid)
        response.setHeader('Content-Type', 'text/javascript')
        return """
// Javascript summary of a Pleiades entity
var pleiades_oljs = %s;
        """ % geojson.dumps(
                dict(
                    uid=self.context.UID(),
                    where=where,
                    centroid=centroid
                    )
                )

GMAPS_KEY = os.environ.get('GMAPS_KEY', '')

class GoogleAPIKey(BrowserPage):

    def __call__(self):
        return GMAPS_KEY


class EditGeo(BrowserPage):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.transform = Transform(PROJ_900913)

    def __call__(self):
        """Request parameters are 'type' and 'coordinates'."""
        request = self.request
        response = request.response
        try:
            gtype = request.form.get('type')
            coords = request.form.get('coordinates')
            data = '{"type": "%s", "coordinates": %s}' % (gtype, coords)
            obj = geojson.loads(data, object_hook=geojson.GeoJSON.to_instance)
        except:
            raise
            response.setStatus(400)
            return "Input geometry is not acceptable"
        
        # Input is 900913, transform back to lon/lat
        result = self.transform(obj, inverse=True)        
        g = IGeoreferenced(self.context)
        g.setGeoInterface(result.type, result.coordinates)
        notify(ObjectGeoreferencedEvent(g))

        if request.get('HTTP_REFERER'):
            response.redirect(request.get('HTTP_REFERER').split('?')[0] + '?portal_status_message=Changes%20saved.')
        else:
            response.setStatus(200)
            return "Geometry edited successfully"

