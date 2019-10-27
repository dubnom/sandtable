from math import radians, sin, fabs
from sandable import Sandable
from dialog import DialogFloat, DialogBreak


class Sander(Sandable):
    """
### Pretty curves that describe complex harmonic motion

#### Hints

Check out the Wikipedia description of the [Lissajous Curve](http://en.wikipedia.org/wiki/Lissajous_curve).

#### Parameters

* **A and B Frequencies** - the ratio that describes the harmonic is very sensitive to A/B.
  If **A** == **B** and **Delta** == 0 then the ratio is 1 and a line is drawn.
  If **A** == **B** and **Delta** == 90 an elipse will be drawn.
  Setting **A**=1 and **B**=2 will draw a figure eight.
  Play with the numbers to make pretty looping patterns (try **A**=2 and **B**=5).
* **Delta** - is the X angular offset.  Try setting **Delta** to one of these numbers: 0, 30, 45, 90.
  Other numbers are interesting as well.
* **X and Y Center** - where the center of the figure will be relative to the table. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
"""

    EPSILON = 1E-4

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("aFreq",           "A Frequency",          default=8.0, min=0.001, max=100.0, rRound=0),
            DialogFloat("bFreq",           "B Frequency",          default=9.0, min=0.001, max=100.0, rRound=0),
            DialogFloat("delta",           "Delta",                units="degrees", default=0.0),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
            DialogFloat("width",           "Width (x)",            units=units, default=width, min=1.0, max=1000.0),
            DialogFloat("length",          "Length (y)",           units=units, default=length, min=1.0, max=1000.0),
        ]

    def generate(self, params):
        xScale = params.width / 2.0
        yScale = params.length / 2.0
        res = 0.25

        chain = []
        for p in range(10000):
            xPoint = params.xCenter + xScale * sin(radians(res * p * params.aFreq + params.delta))
            yPoint = params.yCenter + yScale * sin(radians(res * p * params.bFreq))
            chain.append((xPoint, yPoint))
            if len(chain) > 4 and self._closeEnough(chain[0], chain[-2]) and self._closeEnough(chain[1], chain[-1]):
                break

        return [chain]

    def _closeEnough(self, p1, p2):
        return fabs(p1[0] - p2[0]) < self.EPSILON and fabs(p1[1] - p2[1]) < self.EPSILON
