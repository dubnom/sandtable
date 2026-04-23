from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

def shrinky(chains, iterations, amount):
    for i in range(iterations):
        allPolys = Polygon()
        for chain in chains:
            if len(chain) < 3:
                continue
            p = Polygon(chain)
            try:
                allPolys = allPolys.union(p)
            except Exception:
                pass

        newChains = []
        def recursiveShrink(poly):
            buf = poly.buffer(amount)
            if buf.geom_type == 'MultiPolygon':
                for poly2 in buf.geoms:
                    recursiveShrink(poly2)
            else:
                if buf.exterior:
                    newChains.append([p for p in buf.exterior.simplify(0.1, True).coords])
        recursiveShrink(allPolys)
        chains = newChains
        yield newChains
