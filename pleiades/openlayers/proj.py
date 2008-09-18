import geojson
from pyproj import Proj


PROJ_900913 = """
+proj=merc +a=6378137 +b=6378137
+lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0
+units=m +nadgrids=@null +no_defs
"""


class Transform(object):
    
    def __init__(self, proj_defn):
        self.proj = Proj(proj_defn)

    def __call__(self, ob, inverse=False, object_hook=None):
        """Transform an object which provides the geo interface from 
        geographic to projected coordinates.
        
        If the inverse keyword is True, pyproj computes the inverse transform.

        If an object_hook callable is provided (as in geojson), instances of
        a particular class will be returned. Otherwise instances of geojson
        geometry classes are returned.
        """
        geo = getattr(ob, '__geo_interface__', ob)
        constructor = object_hook or geojson.GeoJSON.to_instance
        return constructor(self.transform_geom(geo, inverse))

    def transform_coords1(self, coords, inverse=False):
        x, y = self.proj(*tuple(coords), **dict(inverse=inverse))
        return (x, y)

    def transform_coords2(self, coords, inverse=False):
        lons, lats = zip(*coords)
        xs, ys = self.proj(lons, lats, **dict(inverse=inverse))
        return tuple(zip(xs, ys))

    def transform_coords3(self, coords, inverse=False):
        return tuple([self.transform_coords2(r, inverse) for r in coords])
        
    def transform_coords4(self, coords, inverse=False):
        return tuple([self.transform_coords3(p, inverse) for p in coords])
    
    def transform_geom(self, geo, inverse=False):
        gtype = geo['type']
        coords = geo['coordinates']
        if gtype == 'Point':
            result = self.transform_coords1(coords, inverse)
        elif gtype in ['LineString', 'LinearRing', 'MultiPoint']:
            result = self.transform_coords2(coords, inverse)
        elif gtype in ['Polygon', 'MultiLineString']:
            result = self.transform_coords3(coords, inverse)
        elif gtype == 'MultiPolygon':
            result = self.transform_coords4(coords, inverse)
        else:
            raise NotImplemented, "No geometry collections in this version"
        return dict(type=gtype, coordinates=result)
