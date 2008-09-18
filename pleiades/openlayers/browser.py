import os
from shapely.geometry import asShape
from pyproj import Proj
from zope.publisher.browser import BrowserPage
from zgeo.geographer.interfaces import IGeoreferenced


PROJ_900913 = """
+proj=merc +a=6378137 +b=6378137
+lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0
+units=m +nadgrids=@null +no_defs
"""

class OLSphericalMercatorJS(BrowserPage):
    """Returns coordinates projected to Spherical Mercator for use with 
    Google Maps.
    """
    def __call__(self):
        response = self.request.response
        geo = IGeoreferenced(self.context)
        
        # Project the geo coordinates
        proj_sm = Proj(PROJ_900913)
        if geo.type == 'Point':
            x, y = proj_sm(*tuple(geo.coordinates))
            where = dict(type=geo.type, coordinates=[x, y])
            centroid = where
        else:
            #shape = asShape(geo)
            #centroid = shape.centroid
            raise NotImplemented, "Points only in this version"

        response.setHeader('Content-Type', 'text/javascript')
        return """
// Javascript summary of a Pleiades entity
var pleiades_oljs = %s;
        """ % dict(
                uid=self.context.UID(),
                where=where,
                centroid=centroid
                )


GMAPS_KEY = os.environ.get('GMAPS_KEY', '')

class GoogleAPIKey(BrowserPage):

    def __call__(self):
        return GMAPS_KEY


class EditGeo(BrowserPage):
    pass
    
