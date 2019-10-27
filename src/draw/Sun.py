from sandable import Sandable
from dialog import DialogInt, DialogFloat, DialogYesNo, DialogBreak
from Chains import Chains
from math import radians, sin, cos


class Sander(Sandable):
    """
### Draw figures that roughly resembles the sun and its rays

#### Hints

Set **Ray width**=0 for a cool effect.

#### Parameters
* **Ray count** - number of rays.
* **Ray width** - width in degrees of each ray.
* **Ripples** - number of waves in a ray.
* **X Center** and **Y Center** - where the center of the sun will be relative to the table.
* **Inner radius** and **Outer radius** - how far from the center the rays should start and end.
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        rippleSize = min(width, length) * .05
        radius = max(width, length) / 2.0
        self.editor = [
            DialogInt("rays",            "Ray count",            default=12, min=1, max=60),
            DialogInt("rayWidth",        "Ray width",            units="degrees", default=10, min=1, max=60),
            DialogFloat("ripples",         "Number of ripples",   default=2.0, min=0.0, max=20.0),
            DialogFloat("rippleSize",      "Size of ripples",      units=units, default=rippleSize, min=0., max=3*rippleSize),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
            DialogFloat("innerRadius",     "Inner radius",         units=units, default=2.0, min=0.0, max=radius),
            DialogFloat("outerRadius",     "Outer radius",         units=units, default=min(width, length)/2, min=1.0, max=radius),
        ]

    def generate(self, params):
        self.xCenter = params.xCenter
        self.yCenter = params.yCenter

        self.rayMax = 360
        self.rayStep = 20
        self.rayScale = params.outerRadius - params.innerRadius
        self.innerRadius = params.innerRadius

        self.ripples = params.ripples
        self.rippleSize = params.rippleSize

        raySpacing = 360.0 / params.rays

        chain = []
        for ray in range(params.rays):
            angle = ray * raySpacing
            chain.extend(self.ray(angle, 1))
            chain.extend(self.ray(angle + params.rayWidth, -1))
        chain.append(chain[0])
        if params.fitToTable:
            chain = Chains.circleToTable(chain, self.width, self.length)
        return [chain]

    def ray(self, angle, dir):
        chain = []
        for r in range(0, self.rayMax, self.rayStep):
            x = self.innerRadius + self.rayScale * r / self.rayMax
            y = self.rippleSize * sin(radians(r * self.ripples))
            ar = radians(angle)
            xPoint = self.xCenter + (x * cos(ar)) - (y * sin(ar))
            yPoint = self.yCenter + (x * sin(ar)) + (y * cos(ar))
            chain.append((xPoint, yPoint))
        if dir < 0:
            chain.reverse()
        return chain
