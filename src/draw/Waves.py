from sandable import Sandable, inchesToUnits
from math import radians, sin
from dialog import DialogFloat, DialogInt, DialogBreak


class Sander(Sandable):
    """
### Draw waves

#### Hints

Try changing **Shift per line** first.

#### Parameters

 * **Wave Height** - height of each of the waves.
 * **Lines** - number of horizontal wave lines.
 * **Points per line** - number of points that make up each line.
 * **Waves per Line** - number of waves per horizontal line.
 * **Shift per Line** - amount to shift waves over each line.
 * **Wave increment** - percent to increase/decrease number of waves for each line.
   Very small changes from a 100% yield large changes to the number of waves since
   the effect is cumulative for each line.
 * **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
 * **Width** and **Length** - how big the figure should be. Probably not worth changing.
 """

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("wHeight",         "Wave Height",          units=units, default=inchesToUnits(1.0, units), min=0.0, max=length),
            DialogInt("lines",           "Lines",                default=40, min=5, max=100),
            DialogInt("xCount",          "Points per line",      default=100, min=10, max=160),
            DialogFloat("waves",           "Waves per Line",       default=3.0, min=0.0, max=45.0),
            DialogFloat("shift",           "Shift per Line",       units="degrees", default=5.0, min=0.0, max=10.0),
            DialogFloat("increment",       "Wave increment",       units="percent", default=100.0, min=95.0, max=105.0),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",             units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",             units=units, default=0.0),
            DialogFloat("width",           "Width",                units=units, default=width, min=1.0, max=1000.0),
            DialogFloat("length",          "Length",               units=units, default=length, min=1.0, max=1000.0),
        ]

    def generate(self, params):
        xCount = params.xCount
        xScale = params.width / xCount

        xyScale = (360.0 * params.waves) / xCount
        yCount = params.lines
        yScale = params.length / params.lines
        waveMultiplier = 1.0
        increment = params.increment * 0.01

        chains = []
        for y in range(0, yCount):
            chain = []
            for x in range(xCount):
                xPoint = params.xOffset + x * xScale
                yPoint = params.yOffset + y * yScale + params.wHeight * sin(radians(waveMultiplier * x * xyScale + y * params.shift))
                chain.append((xPoint, yPoint))
            if y % 2:
                chain.reverse()
            chains.append(chain)
            waveMultiplier *= increment

        return chains
