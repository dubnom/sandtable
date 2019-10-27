from math import sqrt
import random
from sandable import Sandable, inchesToUnits
from dialog import DialogInt, DialogBreak, DialogFloat
from Chains import Chains


class Sander(Sandable):
    """
### Randomly generate something that looks like a wood board

#### Hints

Drawing random wood boards requires a lot of compute time. Be patient.

#### Parameters

* **Number of Knots** - number of knots that the piece of wood should have.
* **Maximum Knot Radius** - largest radius of a random knot.
* **Random seed** - used to generate random drawings.  Different seeds generate different locations
  and sizes for the knots. The *Random* button will create new seeds automatically.
* **Number of points/line** - The smoothness of the wood grain lines.
* **Number of lines** - Number of grain lines..
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogInt("knots",           "Number of Knots",          default=5, min=0, max=20),
            DialogFloat("rKnot",           "Maximum Knot Radius",      units=units, default=inchesToUnits(
                5.0, units), min=inchesToUnits(1.0, units), max=max(width, length)),
            DialogInt("seed",            "Random seed",              default=1, min=0, max=10000, rbutton=True),
            DialogInt("xLines",          "Number of points/line",    default=200, min=50, max=600),
            DialogInt("yLines",          "Number of lines",          default=40, min=5, max=100),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",                 units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",                 units=units, default=0.0),
            DialogFloat("width",           "Width (x)",                units=units, default=width),
            DialogFloat("length",          "Length (y)",               units=units, default=length),
        ]

    def generate(self, params):
        random.seed(params.seed)
        knots = []
        attempts = 200
        knotTurns = 6
        while len(knots) < params.knots and attempts > 0:
            r = random.random() * params.rKnot
            x = params.xOffset + r + random.random()*(params.width-(2*r))
            y = params.yOffset + r + random.random()*(params.length-(2*r))
            # Check for circular overlap
            for knot in knots:
                if self._overlap(x, y, r, knot):
                    attempts -= 1
                    break
            else:
                knots.append(((x, y), r))
        knots.sort(key=lambda chain: chain[0][0])

        chains = self._grid(params)
        for c, s in knots:
            self._knot(chains, c, s)
            chains.insert(0, Chains.spiral(c[0], c[1], 0., s, knotTurns))
        chains.insert(len(knots), [(params.xOffset+params.width, params.yOffset)])
        return chains

    def _grid(self, params):
        xCount = params.xLines
        yCount = params.yLines
        xSpacing = params.width / xCount
        ySpacing = params.length / yCount

        chains = []
        for y in range(yCount + 1):
            yp = params.yOffset + y * ySpacing
            chain = [[params.xOffset + x * xSpacing, yp] for x in range(xCount + 1)]
            if y % 2:
                chain.reverse()
            chains.append(chain)
        return chains

    def _knot(self, chains, knotCenter, knotRadius):
        for chain in chains:
            for point in chain:
                distance = sqrt((knotCenter[0]-point[0]) ** 2 + (knotCenter[1]-point[1]) ** 2)
                if distance > 0.01:
                    point[0] += knotRadius * ((point[0] - knotCenter[0]) / distance)
                    point[1] += knotRadius * ((point[1] - knotCenter[1]) / distance)

    def _overlap(self, x1, y1, r1, rock):
        ((x2, y2), r2) = rock
        dx, dy = x2 - x1, y2 - y1
        return sqrt(dx**2 + dy**2) < (r1 + r2)
