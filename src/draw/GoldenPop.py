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
            DialogFloat("circleDiameter",  "Circle Diameter",      units=units, default=3.),
            DialogInt("iterations",        "Iterations",           default=60, min=1, max=200),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
        ]

    def generate(self, params):
        xCenter = params.xCenter
        yCenter = params.yCenter
        radius = params.radius
        reduction = params.reductionRate
        circleRadius = params.circleDiameter / 2.

        def pnt(angle, radius):
            x = cos(radians(angle)) * radius
            y = sin(radians(angle)) * radius
            return x,y

        angle = 0.
        chain = [(xCenter, yCenter)]
        for i in range(params.iterations):
            x,y = pnt(angle, radius-circleRadius)
            x += xCenter
            y += yCenter
            chain.append( (x,y) )
            xc, yc = pnt(angle, radius)
            xc += xCenter
            yc += yCenter
            for a in range(0,360,15):
                x1,y1 = pnt(180+a+angle, circleRadius)
                chain.append( (x1+xc, y1+yc))
            chain.append( (x, y) )
            chain.append( (xCenter, yCenter) )

            angle += params.angle
            radius *= reduction
            circleRadius *= reduction

        return [chain]

