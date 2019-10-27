from math import radians, sin, cos, exp, pi, sqrt
from sandable import Sandable
from dialog import DialogFloat, DialogYesNo, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### Nautilus spiral

The Nautilus or [Logarithmic spiral](https://en.wikipedia.org/wiki/Logarithmic_spiral) can draw many shapes commonly found in nature.

#### Parameters
* **Inner radius** - Radius of the inside of the spiral.
* **Turns** - Number of turns of the spiral.
* **Sample rate** - Angular distance between points on the spiral.
* **Curve factor** - Amount of curvature of the arc that makes up chambers.
* **Scale factor** - Speed of exponential growth.
* **Logarithmic growth** - Percent of exponential growth per chamber.
* **Fit to table** - map circular patterns to the shape of the table.
* **X Center** and **Y Center** - where the center of the spiral will be relative to the table.
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.editor = [
            DialogFloat("innerRadius",     "Inner radius",         units=units, min=0.0, max=min(width, length) / 2.),
            DialogFloat("turns",           "Turns",                default=5., min=1.0, max=50.0),
            DialogFloat("angleRate",       "Sample rate",          units="degrees", default=11.0, min=1, max=45.0),
            DialogFloat("curveFactor",     "Curve factor",         default=1., min=-6., max=6.),
            DialogFloat("scaleFactor",     "Scale factor",         default=1., min=.01, max=10.0),
            DialogFloat("logGrowth",       "Logarithmic growth",   units="percent", default=0., min=0., max=2.),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
        ]
        self.maxRadius = 2. * sqrt(width**2 + length**2)

    def generate(self, params):
        xCenter = params.xCenter
        yCenter = params.yCenter

        angleRate = params.angleRate
        points = int(params.turns * 360.0 / angleRate)
        curveAngle = radians(angleRate * params.curveFactor)
        growth = .2 * params.scaleFactor
        angleGrowth = 1.0 + params.logGrowth * .01

        def pnt(angle, offset):
            radius = exp((angle+offset)*growth) + params.innerRadius
            if radius > self.maxRadius:
                raise OverflowError()
            x = xCenter + cos(angle) * radius
            y = yCenter + sin(angle) * radius
            return (x, y)

        chain = []
        for point in range(points):
            pchain = []
            angle = radians(point * angleRate)
            angleRate *= angleGrowth

            try:
                pchain.append(pnt(angle, 0))
                pchain.append(pnt(angle-curveAngle, -.5*pi))
                pchain.append(pnt(angle-curveAngle, -1.5*pi))
                pchain.append(pnt(angle-2.*pi, 0.))
                nchain = Chains.Spline(pchain)
                chain += nchain
                nchain.reverse()
                chain += nchain
            except OverflowError:
                break

        if params.fitToTable:
            chain = Chains.circleToTable(chain, self.width, self.length)
        return [chain]
