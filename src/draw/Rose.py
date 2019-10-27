from math import radians, sin, cos
from sandable import Sandable
from dialog import DialogFloat, DialogInt, DialogYesNo, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### Draw rose curves (pretty flowerlike drawings)

### Hints

Read the Wikipedia article on [Rose (mathematics)](http://en.wikipedia.org/wiki/Rose_(mathematics)).

#### Parameters

* **Petals** - number of petals in the flower.
* **Starting angle** - amount to rotate the flower.
* **Shift angle** - amount to rotate each subsequent petal.
* **Sample rate** - how frequently to draw a point when going around the flower.
* **Turns** - number of lines per petal.
* **X Center** and **Y Center** - where the center of the flower will be relative to the table.
* **Inner radius** and **Outer radius** - how far from the center the should start and end.
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        radius = min(width, length) / 2.0
        mRadius = max(width, length) / 2.0
        self.editor = [
            DialogFloat("petals",          "Petals",               default=7.0, min=0.001, max=45.0),
            DialogFloat("angleStart",      "Starting angle",       units="degrees", min=-180., max=180.),
            DialogFloat("angleShift",      "Shift angle",          units="degrees", default=0.0, min=-10.0, max=10.0),
            DialogFloat("angleRate",       "Sample rate",          units="degrees", default=3.0, min=1.0, max=10.0),
            DialogInt("turns",           "Turns",                default=20, min=1, max=int(mRadius/ballSize * 4)),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
            DialogFloat("innerRadius",     "Inner radius",         units=units, default=radius * .15, min=0.0, max=mRadius),
            DialogFloat("outerRadius",     "Outer radius",         units=units, default=radius, min=1.0, max=mRadius),
        ]

    def generate(self, params):
        chain = []
        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius
        if params.angleRate:
            xCenter = params.xCenter
            yCenter = params.yCenter
            k = params.petals / 2.0

            thickness = params.outerRadius - params.innerRadius
            lines = params.turns
            points = int(360.0 / params.angleRate)
            angleStart = radians(params.angleStart)
            for line in range(lines):
                inRadius = params.innerRadius
                outRadius = thickness * float(line) / float(lines)
                for point in range(points):
                    angle = radians(point * params.angleRate)
                    radius = inRadius + outRadius * abs(sin(k * angle))
                    angle += angleStart
                    x = xCenter + (cos(angle) * radius)
                    y = yCenter + (sin(angle) * radius)
                    chain.append((x, y))
                angleStart += radians(params.angleShift)
        if params.fitToTable:
            chain = Chains.circleToTable(chain, self.width, self.length)
        return [chain]
