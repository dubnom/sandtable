from sandable import Sandable, SandException
from dialog import DialogInts, DialogInt, DialogFloat, DialogBreak, DialogYesNo
from Chains import Chains
from functools import reduce
from math import pi, sin, cos


class Sander(Sandable):
    """
### Draw patterns similar to the Spirograph toy

A Spirograph is a geared toy where a gear wheel with a pen in it goes around (either inside or outside) another gear.
This relatively simple arrangement is capable of drawing interesting geometric patterns. The SandTable takes this idea a
bit further and allows an arbitrary number of gears to be used.

#### Hints

Simpler wheel teeth ratios produce simpler patterns. Prime numbers can take a long time.

#### Parameters

* **X Center** and **Y Center** - where the center of the drawing will be relative to the table.
  Usually not worth changing.
* **Radius** - how big the drawing should be. This shouldn't need changing but it is sometimes fun
  to pick larger numbers to zoom in.
* **Wheel Teeth** - a list of gears and their teeth.  The first number is a fixed gear, each subsequent
  gear orbits the previous gear. If the number of teeth is positive, the gear orbits on the outside, negative
  is on the inside.  Generally, the more wheels the more complex the image (and the longer it will take to generate).
  **Wheel Teeth** is the parameter that is most interesting to change. Gear teeth can only be integers and
  they are separated in the list by commas.
* **Resolution** - how fine the curves are. Smaller numbers are more boxy while larger numbers make rounder curves.

#### Examples

Description | Wheel Teeth | Resolution
--- | --- | ---
Clover | 40,-30 | 7
Inner Clover | 40,30 | 9
Detailed Triangle | 100,-33 | 5
Detailed 3-Lobes | 100,33 | 5
Prickly Cross | 40,-30,-5 | 7
Four Clouds | 40,-30,5 | 7
Sand Dollar | 50,12,-4 | 7
"""

    MAX_POINTS = 25000

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.editor = [
            DialogInts("teeths",          "Wheel Teeth",              units="n1,n2,...", default=[40, -30], min=-60, max=60, minNums=2, maxNums=3),
            DialogInt(	 "resolution",      "Resolution",               default=7, min=1, max=60),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",                 units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",                 units=units, default=length / 2.0),
            DialogFloat("radius",          "Radius",                   units=units, default=min(width, length)/2, min=1.0),
        ]

    def generate(self, params):
        # Get the number of teeth, renormalize based on common divisor, calculate radii
        teeth = params.teeths
        teeth = [t for t in teeth if t]
        if len(teeth) == 0:
            raise SandException("There needs to be at least one number for Wheel Teeth")

        teeth[0] = abs(teeth[0])

        gcd = abs(self.gcdList(teeth))
        teeth = [int(tooth/gcd) for tooth in teeth]
        radii = [tooth / (2.0 * pi) for tooth in teeth]

        # Ratios are all relative to the inner most gear which is 1
        ratios = [0] * len(teeth)
        tp = len(teeth) - 1
        ratios[tp] = 1.0
        while tp > 0:
            tp -= 1
            ratios[tp] = ratios[tp+1] * float(teeth[tp+1]) / teeth[tp]

        # Number of points is based on the lowest common multiple of all of the teeth
        points = self.lcmList(teeth)
        resolution = params.resolution if points * params.resolution < self.MAX_POINTS else self.MAX_POINTS / float(points)
        points = int(points * resolution)
        mult = (2.0 * pi) / float(params.resolution * min([abs(t) for t in teeth]))

        chain = []
        for tooth in range(points + 1):
            a = 0.0
            x, y = params.xCenter, params.yCenter
            for r, rat in zip(radii, ratios):
                a += rat * tooth * mult
                x += r * cos(a)
                y += r * sin(a)
            chain.append((x, y))
        chains = Chains.autoScaleCenter([chain], [(params.xCenter-params.radius, params.yCenter-params.radius),
                                                  (params.xCenter+params.radius, params.yCenter+params.radius)])
        if params.fitToTable:
            chains = [Chains.circleToTable(c, self.width, self.length) for c in chains]
        return chains

    def gcd(self, a, b):
        """Geatest Common Divisor - Euclid"""
        while b:
            a, b = b, a % b
        return a

    def lcm(self, a, b):
        """Lowest Common Multiple"""
        return a * b // self.gcd(a, b)

    def gcdList(self, numbers):
        """Greatest Common Divisor for a list of numbers"""
        return reduce(self.gcd, numbers)

    def lcmList(self, numbers):
        """Lowest Common Multiple for a list of numbers"""
        return reduce(self.lcm, numbers)
