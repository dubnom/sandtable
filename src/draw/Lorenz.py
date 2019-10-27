from sandable import Sandable
from dialog import DialogFloat, DialogInt, DialogBreak
from Chains import Chains
import math


class Sander(Sandable):
    """
### Draw a Lorenz Attractor (a type of fractal)

#### Hints

Read the Wikipedia article on [Lorenz Systems](http://en.wikipedia.org/wiki/Lorenz_system)

#### Parameters

* **h, a, b, c** - coefficients that describe parameters for the chaotic differential equations.
* **Number of points** - number of points to draw in the Lorenz curve.
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("h",               "Coefficient 'H'",          default=0.01, min=.001, max=.05),
            DialogFloat("a",               "Coefficient 'A'",          default=10.0, min=.5, max=45.0),
            DialogFloat("b",               "Coefficient 'B'",          default=28.0, min=.5, max=45.0),
            DialogFloat("c",               "Coefficient 'C'",          default=8.0 / 3.0, min=.1, max=5.0),
            DialogInt("points",          "Number of points",         default=5000),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",                 units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",                 units=units, default=0.0),
            DialogFloat("width",           "Width",                    units=units, default=width, min=1.0, max=1000.0),
            DialogFloat("length",          "Length",                   units=units, default=length, min=1.0, max=1000.0),
        ]

    def generate(self, params):
        x0 = 0.1
        y0 = 0.0
        z0 = 0.0

        h = params.h
        a = params.a
        b = params.b
        c = params.c

        chain = []
        for i in range(params.points):
            x1 = x0 + h * a * (y0 - x0)
            y1 = y0 + h * (x0 * (b - z0) - y0)
            z1 = z0 + h * (x0 * y0 - c * z0)
            x0, y0, z0 = x1, y1, z1
            if math.isinf(x0) or math.isnan(x0) or math.isinf(y0) or math.isnan(y0):
                break
            chain.append((x0, y0))

        # Rescale chain
        extents = [(params.xOffset, params.yOffset), (params.xOffset + params.width, params.yOffset + params.length)]
        return Chains.fit([chain], extents)
