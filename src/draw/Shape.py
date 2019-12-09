from random import random
from math import sin, cos, radians

from dialog import DialogInt, DialogFloat, DialogBreak
from Chains import Chains
from sandable import Sandable, SandException


class Sander(Sandable):
    """
### Create a polygon with some randomness and rotate it in or out

#### Params
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.editor = [
            DialogInt("points",             "Polygon points",       default=10, min=3, max=50),
            DialogInt("interp",             "Interpolated points",  default=5, min=0, max=10),
            DialogFloat("randomness",       "Randomness",           units="percent", default=10., min=0., max=100.),
            DialogFloat("rotation",         "Rotation",             units="degrees", default=0., min=-180., max=180.),
            DialogBreak(),
            DialogInt("polygons",           "Polygon Count",        default=10, min=1, max=100),
            DialogFloat("r1",               "First radius",         units=units, min=0.0, max=max(width, length)*2),
            DialogFloat("r2",               "Second radius",        units=units,  default=min(width, length)/2, min=0.0, max=max(width, length)*2),
            DialogBreak(),
            DialogFloat("xCenter",          "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",          "Y Center",             units=units, default=length / 2.0),
        ]

    def generate(self, params):
        # Make the shape (centered on 0,0 and a radius from 0 to 1.)
        rotateAngle = 360. / params.points
        polygon = []
        for point in range(params.points):
            angle = radians(rotateAngle * point)
            radius = .5 + (random()-.5) * (params.randomness / 100.)
            polygon.append((cos(angle) * radius, sin(angle) * radius))

        # Treat the points in the polygon as base points for splines
        polygon = Chains.Spline(chain, expansion=params.interp)

        # Grow/shrink and rotate polygon
        scaleFactor = (params.r2 - params.r1) / params.polygons
        chains = []
        for i in range(params.polygons):
            angle = params.rotation * i
            scale = params.r1 + i * scaleFactor
            chains.append( Chains.scale(Chains.rotate([polygon], scale), angle)[0] )

        # Center based on user coordinates
        chains = Chains.transform(chains, (params.xCenter, params.yCenter))

        return chains

