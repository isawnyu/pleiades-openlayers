from collective.geo.geographer.event import ObjectGeoreferencedEvent
from collective.geo.geographer.interfaces import IGeoreferenced
from pleiades.openlayers.proj import Transform, PROJ_900913
from shapely.geometry import asShape
from zope.event import notify
from zope.publisher.browser import BrowserPage
import geojson
import os


class OLSphericalMercatorJS(BrowserPage):
    """Returns coordinates projected to Spherical Mercator.

    For use with Google Maps.
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
        context_url = self.context.absolute_url()
        response.setHeader('Content-Type', 'text/javascript')
        return """
// Javascript summary of a Pleiades entity
var url_marker_gold = "%s/++resource++marker_gold.png";
var url_marker_shadow = "%s/++resource++marker_shadow.png";
var pleiades_oljs = %s;
        """ % (
            context_url,
            context_url,
            geojson.dumps({
                'uid': self.context.UID(),
                'where': where,
                'centroid': centroid,
            })
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
