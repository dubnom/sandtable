from math import radians, sin
from sandable import Sandable, inchesToUnits
from dialog import DialogFloat, DialogBreak


class Sander(Sandable):
    """
### Draw a pattern that looks like roofing shingles

#### Hints

This is a pretty boring pattern. Try something more fun.

#### Parameters

* **Shingle Height** - the height of each individual shingle.
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("sHeight",         "Shingle Height",       units=units, default=inchesToUnits(
                2, units), min=inchesToUnits(0.1, units), max=inchesToUnits(5, units)),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",             units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",             units=units, default=0.0),
            DialogFloat("width",           "Width (x)",            units=units, default=width),
            DialogFloat("length",          "Length (y)",           units=units, default=length),
        ]

    def generate(self, params):
        pointsPerShingle = 11
        yScale = params.sHeight
        lines = int(params.length / yScale)
        shingles = params.width / params.sHeight
        pointCount = int(shingles * pointsPerShingle)
        xScale = params.width / pointCount
        angleMult = 90.0 / pointsPerShingle

        chain = []
        points = list(range(pointCount))
        for line in range(lines):
            yOffset = params.yOffset + line * yScale
            offset = (line % 2) * 90.0
            for point in points:
                angle = radians(offset + (point * angleMult))
                x = params.xOffset + (point * xScale)
                y = yOffset + (abs(sin(angle)) * yScale)
                chain.append((x, y))
            points.reverse()

        return [chain]
