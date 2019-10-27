from math import radians, sin, cos, pow
from sandable import Sandable, inchesToUnits
from dialog import DialogFloat, DialogFloats, DialogYesNo, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### Draw interfering sine waves around a spiral

#### Parameters

* **Turns** - number of lines drawn within the spiral.
* **Starting angle** - the angle the spiral starts at. The default of 0.0 starts to the right of center.
* **Sample rate** - how frequently points are calculated around the spiral.  Smaller numbers create rounder
  spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
  121 to get a rotating triangle; 74 makes a rotating pentagon.
* **Growth base power** - how quickly the outer rings of the spiral get farther from each other.
  The default of 1.0 creates a linear spiral, try 2.0 or more for a spiral that grows faster
  and 0.5 for a spiral that is big in the center.
* **Wave frequency(s)** - a list of wave frequencies, or more simply put - the number of waves for each
  rotation of the spiral.  If the number is an integer, the number of waves will remain in place from line-to-line.
  Non-integers will draw the whole-number of waves and leave a bit over for the decimal. If the number isn't too far from
  an integer it will look like a slowly rotating figure. If the number is further away, the figure will rotate quickly
  and create patterns that "interfere" with one another (in a pleasant way).
  More than one frequency can be given. When this is combined with different **Wave amplitudes** and **Wave phases**
  complex and interesting figures emerge.
* **Wave amplitude(s)** - the height of each wave.
* **Wave phase(s)** - the starting phase, in degrees, of each wave.
* **Inner radius** and **Outer radius** - how far from the center the spiral should start and end.
* **X Center** and **Y Center** - where the center of the spiral will be relative to the table.

#### Examples

Description | LPI | Start | Sample | Growth | Freqs | Amps | Phases | Inner | Outer
--- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Spiraling Boxy | 5 | 0 | 5 | 1 | 4.1 | 1 | 0 | 1 | 8
Gentler Boxy | 3 | 0 | 5 | 1 | 4.05 | 1 | 0 | 1 | 8
Wobbly Boxy | 1 |  0 | 5 | 1 | 4.05, 7 | 1, .5 | 0 | 0 | 1 | 8
Spiky | 1 |  0 | 5 | 1 | 24 | 1 | 0 | 1 | 8
Messy Triangle | 1.25 | 0 | 5 | 1 | 3.1, 25.5 | 1, .5 | 0 | 0 | 1 | 8
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        radius = min(width, length) / 2.0
        mRadius = max(width, length) / 2.0
        self.editor = [
            DialogFloat("turns",           "Turns",                default=10, min=1, max=max(width, length)*4),
            DialogFloat("angleStart",      "Starting angle",       units="degrees"),
            DialogFloat("angleRate",       "Sample rate",          units="degrees", default=5.0),
            DialogFloat("base",            "Growth base power",    default=1.0, min=0.001),
            DialogFloats("frequencies",     "Wave frequency(s)",    units="f1,f2,...", default=[6, 30], min=1.0, max=60.0, minNums=1, maxNums=3),
            DialogFloats("amplitudes",      "Wave amplitude(s)",    units="%s a1,a2,..." %
                         units, default=[1, .5], min=0.1, max=inchesToUnits(2.0, units), minNums=1, maxNums=3),
            DialogFloats("phases",          "Wave phase(s)",        units="degrees p1,p2,...",
                         default=[0, 0], min=0.0, max=360.0, minNums=1, maxNums=3, rRound=0),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
            DialogFloat("innerRadius",     "Inner radius",         units=units, default=radius * 0.15, min=0.0, max=mRadius),
            DialogFloat("outerRadius",     "Outer radius",         units=units, default=radius, min=1.0, max=mRadius),
        ]

    def generate(self, params):
        frequencies = params.frequencies
        amplitudes = params.amplitudes
        phases = params.phases
        fap = list(zip(frequencies, amplitudes, list(map(radians, phases))))

        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius

        chain = []
        if params.angleRate:
            xCenter = params.xCenter
            yCenter = params.yCenter

            thickness = params.outerRadius - params.innerRadius
            points = int(params.turns * 360.0 / params.angleRate)
            divisor = pow((points * abs(params.angleRate)) / 360.0, params.base)

            for point in range(points):
                angle = params.angleStart + radians(point * params.angleRate)
                radius = params.innerRadius + thickness * (pow(((point * abs(params.angleRate)) / 360.0), params.base) / divisor)
                for f, a, p in fap:
                    radius += sin(angle * f + p) * a
                x = xCenter + (cos(angle) * radius)
                y = yCenter + (sin(angle) * radius)
                chain.append((x, y))
        if params.fitToTable:
            chain = Chains.circleToTable(chain, self.width, self.length)
        return [chain]
