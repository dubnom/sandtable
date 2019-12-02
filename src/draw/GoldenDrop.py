from math import radians, sin, cos, exp, pi, sqrt
from sandable import Sandable
from dialog import DialogFloat, DialogInt, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### GoldenDrop

"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.editor = [
            DialogFloat("radius",          "Starting Radius",      units=units, default=min(width,length)/2., min=3., max=max(width,length)),
            DialogFloat("angle",           "Phyllotaxic Angle",    units="degrees", default=137.51, min=1, max=180.0),
            DialogFloat("reductionRate",   "Reduction Rate",       default=0.976, min=.85, max=.99),
            DialogFloat("petalWidth",      "Petal Width",          units="degrees", default=15., min=5., max=90.),
            DialogInt("iterations",        "Iterations",           default=100, min=1, max=500),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
        ]

    def generate(self, params):
        xCenter = params.xCenter
        yCenter = params.yCenter
        radius = params.radius
        reduction = params.reductionRate
        angleOffset = params.petalWidth / 2.

        def pnt(angle, radius):
            x = cos(radians(angle)) * radius
            y = sin(radians(angle)) * radius
            return x,y

        angle = 0.
        chain = [(xCenter, yCenter)]
        for i in range(params.iterations):
            x,y = pnt(angle-angleOffset, radius)
            chain.append( (x+xCenter, y+yCenter) )
            x,y = pnt(angle+angleOffset, radius)
            chain.append( (x+xCenter, y+yCenter) )
            chain.append( (xCenter, yCenter) )

            angle += params.angle
            radius *= reduction

        return [chain]

