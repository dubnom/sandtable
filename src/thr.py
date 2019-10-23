from math import sqrt, atan2, ceil, sin, cos
from Chains import *

"""
    Thr - Theta Radius files - unit polar coordinates

    Load and save .thr format files.
    Convert chains (polylines) into thr arrays.
"""


def thetaRadius(x, y):
    """ Convert x,y coordinates to theta,radius """
    theta = atan2(y,x)
    radius = sqrt(x*x+y*y)
    return theta, radius

def chainsToThr( chains, minLength=.05 ):
    """ Convert chains to theta,radius array """
    extents =  Chains.calcExtents( chains )

    xr = extents[1][0] - extents[0][0]
    yr = extents[1][1] - extents[0][1]
    rng = .5 * max(xr,yr)
    xl,yl = extents[0][0] + xr/2, extents[0][1] + yr/2

    results = [] 
    x0, y0 = None, None
    for chain in chains:
        for x,y in chain:
            x1,y1 = (x - xl) / rng, (y - yl) / rng
            if x0 != None:
                xd,yd = x1-x0, y1-y0
                # Interpolate the line into minLength units if the line is too large.
                # This is done to create "straight lines" in polar coordinates.
                length = sqrt(xd*xd+yd*yd)
                if length > minLength:
                    add = 1+ceil(length / minLength)
                    xs, ys = xd/add, yd/add
                    for i in range(1,add):
                        results.append( thetaRadius(x0 + xs*i, y0 + ys*i))
            results.append( thetaRadius(x1,y1))
            x0,y0 = x1,y1

    return results

def loadThr( filename, xc=0, yc=0, aplus=0, multiplier=1 ):
    """ Load theta,radius files and scale by optional multiplier """
    chain = []
    with open(filename, 'r') as f:
        while True:
            line = f.readline().strip()
            if len(line) == 0:
                break
            if line.startswith('#'):
                continue
            parts = line.split(' ')
            angle, radius = float(parts[0])+aplus, float(parts[1])
            x, y = xc + sin(angle) * radius * multiplier, yc + cos(angle) * radius * multiplier
            chain += [ (x, y) ]
    return chain


def dumpThr( filename, chains ):
    """ Save theta, radius format to a file """
    with open(filename, 'w') as f:
        for theta, radius in chainsToThr( chains ):
            print( '%.7g %.7g' % (round(theta,7), round(radius,7)), file=f)

