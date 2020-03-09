from math import sin, cos, radians, degrees, atan2
from shapely.geometry import Point, LineString

def boundCircle(chains, center, radius):
    """Bound and clip coordinate using a circle."""

    print("boundCircle", center, radius)
    circle = Point(center[0], center[1]).buffer(radius)
    maxAngle = 3.

    arcStart = None
    x0, y0 = center
    prevPointInCircle = True
    newChains = []
    for chain in chains:
        newChain = []
        for x1,y1 in chain:
            print(x1, y1, '   ', end='')
            pointInCircle = Point(x1,y1).within(circle)
            if pointInCircle and prevPointInCircle:
                # Both points in the circle
                newChain.append((x1,y1))
            elif pointInCircle:
                # Coming in from the outside
                inters = circle.boundary.intersection(LineString([(x0,y0),(x1,y1)]))
                newChain += arcAround(center, arcStart, inters.coords[0], radius, maxAngle)
                newChain.append(inters.coords[0])
                newChain.append((x1,y1))
            elif prevPointInCircle:
                # Leaving the inside
                inters = circle.boundary.intersection(LineString([(x0,y0),(x1,y1)]))
                print(inters.coords[0])
                newChain.append(inters.coords[0])
                arcStart = inters.coords[0]
            else:
                # Both points are outside, check for intersection
                inters = circle.boundary.intersection(LineString([(x0,y0),(x1,y1)]))
                if inters.geometryType() == 'MultiPoint': # Intersection
                    xt0, yt0 = inters.geoms[0].coords[0]
                    xt1, yt1 = inters.geoms[1].coords[0]
                    d0 = (xt0 - x0) ** 2 + (yt0 - y0) ** 2
                    d1 = (xt1 - x0) ** 2 + (yt1 - y0) ** 2
                    print("d0 < d1", d0 < d1, end='' )
                    p0, p1 = (0, 1) if d0 < d1 else (1, 0) 
                    newChain += arcAround(center, arcStart, inters.geoms[p0].coords[0], radius, maxAngle)
                    newChain.append(inters.geoms[p1].coords[0])
                    arcStart = inters.geoms[p1].coords[0]
                elif inters.geometryType() == 'GeometryCollection':
                    # Tangent or terminus
                    pass
                else:
                    # No intersection
                    pass
            x0, y0 = x1, y1
            prevPointInCircle = pointInCircle

        newChains.append(newChain)
    return newChains

def arcAround(center, p0, p1, radius, maxAngle):
    """Run a shortest path arc between two points on a circle."""

    theta0 = degrees(atan2(p0[1] - center[1], p0[0] - center[0]))
    theta1 = degrees(atan2(p1[1] - center[1], p1[0] - center[0]))
    diff = 360 + theta1 - theta0 % 360
    if diff > 180:
        diff = -(360 - diff)
    chain = []
    steps = abs(int(diff / maxAngle)) + 1
    incr = diff / steps
    for step in range(steps+1):
        theta = radians(theta0 + step * incr)
        print('%.4f' % degrees(theta),' ', end='')
        chain.append((center[0] + cos(theta) * radius, center[1] + sin(theta) * radius))
    return chain
