from shapely.geometry import Polygon, MultiPolygon


def shrinky(chains, iterations, amount):
    for i in range(iterations):
        allPolys = None
        for chain in chains:
            if len(chain) < 3:
                continue
            p = Polygon(chain)
            try:
                allPolys = p if not allPolys else allPolys.union(p)
            except Exception:
                pass

        if not allPolys:
            return

        if allPolys.type == 'Polygon':
            allPolys = MultiPolygon([allPolys])

        newChains = []
        for poly in allPolys:
            buf = poly.buffer(amount)
            if buf.type == 'MultiPolygon':
                for poly2 in buf:
                    if poly2.exterior:
                        newChains.append([p for p in poly2.exterior.simplify(0.1, True).coords])
            else:
                if buf.exterior:
                    newChains.append([p for p in buf.exterior.simplify(0.1, True).coords])
        chains = newChains
        yield newChains
