import random
from math import sin, cos, radians

from dialog import DialogInt, DialogFloat, DialogBreak
from Chains import Chains
from sandable import Sandable, SandException


class Sander(Sandable):
    """
### Create a polygon with some randomness and rotate it in or out

#### Parameters

* **Polygon points** - Number of points (or sides) of the starting polygon.
* **Interpolated points** - Number of points to insert to make the sides curvier.
* **Random seed** - Used to generate different random shapes.  The *Random* button will create new seeds (and shapes).
* **Randomness** - Amount of random distortion. *0* creates regular polygons, *100* is the most distorted.
* **Rotation** - Number of degrees to rotate the shape every iteration.
* **Polygon count** - Number of polygons to draw.
* **First radius** and **Second radius** - how far from the center the shape should start and end.
* **X Center** and **Y Center** - where the center of the spiral will be relative to the table.
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.editor = [
            DialogInt("points",             "Polygon points",       default=10, min=3, max=50),
            DialogInt("interp",             "Interpolated points",  default=5, min=0, max=10),
            DialogInt("seed",               "Random seed",          default=1, min=0, max=10000.0, rbutton=True),
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
        random.seed(params.seed)

        # Make the shape (centered on 0,0 and a radius from 0 to 1.)
        rotateAngle = 360. / params.points
        polygon = []
        for point in range(params.points):
            angle = radians(rotateAngle * point)
            radius = .5 + (random.random()-.5) * (params.randomness / 100.)
            polygon.append((cos(angle) * radius, sin(angle) * radius))

        # Treat the points in the polygon as base points for splines
        if params.interp > 0:
            polygon.append(polygon[0])
            polygon = Chains.Spline(polygon, expansion=params.interp)

        # Grow/shrink and rotate polygon
        scaleFactor = (params.r2 - params.r1) / params.polygons
        chains = []
        for i in range(params.polygons):
            angle = params.rotation * i
            scale = params.r1 + i * scaleFactor
            chains.append( Chains.scale(Chains.rotate([polygon], angle), [scale,scale])[0] )

        # Center based on user coordinates
        chains = Chains.transform(chains, (params.xCenter, params.yCenter))

        return chains

