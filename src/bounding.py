from math import sin, cos, radians, degrees, atan2
from shapely.geometry import Point, LineString

def boundCircle(chains, center, radius):
    """Bound and clip coordinate using a circle."""

    circle = Point(center[0], center[1]).buffer(radius)
    maxAngle = 3.

    arcStart = None
    x0, y0 = center             # FIX: This is incorrect
    prevPointInCircle = True    # FIX: This is incorrect
    newChains = []
    for chain in chains:
        newChain = []
        for x1,y1 in chain:
            print(x1, y1, '   ', end='')
            pointInCircle = Point(x1,y1).within(circle)
            if pointInCircle and prevPointInCircle: # Both points in the circle
                print("Both points in the circle")
                newChain.append((x1,y1))
            elif pointInCircle:                     # Coming in from the outside
                print("Coming in from out of the circle")
                inters = circle.boundary.intersection(LineString([(x0,y0),(x1,y1)]))
                newChain += arcAround(center, arcStart, inters.coords[0], radius, maxAngle)
                #newChain.append(inters.coords[0])
                newChain.append((x1,y1))
            elif prevPointInCircle:                 # Leaving the inside
                print("Leaving the inside")
                inters = circle.boundary.intersection(LineString([(x0,y0),(x1,y1)]))
                newChain.append((x1,y1))
                print(inters.coords[0])
                newChain.append(inters.coords[0])
                arcStart = inters.coords[0]
            else:                                   # Both points are outside, check for intersection
                print("Both outside  ", end='')
                inters = circle.boundary.intersection(LineString([(x0,y0),(x1,y1)]))
                if inters.geometryType == 'MultiPoint': # Intersection
                    print("intersection")
                    arcAround(center, arcStart, inters.geoms[0].coords[0], radius, maxAngle)
                    #newChain.append(inters.geoms[0].coords[0])
                    newChain.append(inters.geoms[1].coords[0])
                    arcStart = inters.geoms[1].coords[0]
                elif inters.geometryType == 'Point':    # Tangent or terminus
                    print("tangent")
                    pass
                else:                               # No intersection
                    print("no intersection")
                    pass
            x0, y0 = x1, y1
            prevPointInCircle = pointInCircle

        newChains.append(newChain)
    return newChains

def arcAround(center, p0, p1, radius, maxAngle):
    """Run a shortest path arc between two points on a circle."""

    theta0 = degrees(atan2(p0[1] - center[1], p0[0] - center[0]))
    theta1 = degrees(atan2(p1[1] - center[1], p0[0] - center[0]))
    diff = 360 + theta0 - theta1 % 360
    if diff < 180:
        a0, a1 = theta1, theta0
    else:
        diff = 360 + theta1 - theta0 % 360
        a0, a1 = theta0, theta1
    chain = []
    steps = int(diff / maxAngle) + 1
    incr = diff / steps
    for step in range(steps):
        theta = radians(a0 + step * incr)
        chain.append((center[0] + cos(theta) * radius, center[1] + sin(theta) * radius))
    return chain


foobar = [(x/180., 1.2 * sin(radians(2.*x))) for x in range(-270,270)]
fooman = boundCircle([foobar], (0,0), 1.)
