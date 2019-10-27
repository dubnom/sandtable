from math import radians, sin, cos, pi
from sandable import Sandable
from dialog import DialogFloat, DialogInt, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### Circular pattern with spirals

#### Parameters

* **Radius** - Size of each spiral in the pattern.
* **Rings** - Number of rings of spirals.
* **Turns** - Number of turns that make up each spiral.
* **Sample rate** - how frequently points are calculated around the spiral.  Smaller numbers create rounder
     spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
     121 to get a rotating triangle; 74 makes a rotating pentagon.
* **Spacing factor** - relative distance between spirals.
* **X Center** and **Y Center** - center of the pattern.
"""

    def __init__(self, width, length, ballSize, units):
        radius = min(width, length)*.1
        self.editor = [
            DialogFloat("radius",          "Radius",               units=units, default=radius, min=1.0, max=radius*4),
            DialogInt("rings",           "Rings",                default=3, min=1, max=8),
            DialogFloat("turns",           "Turns",                default=3, min=0.1, max=24.0),
            DialogFloat("angleRate",       "Sample rate",          units="degrees", default=15.0, min=-720.0, max=720.0),
            DialogFloat("factor",          "Spacing factor",       default=1.0, min=.5, max=1.5),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width/2.0, min=0.0, max=width),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length/2.0, min=0.0, max=length),
        ]

    def generate(self, params):
        if not params.angleRate:
            params.angleRate = 15.0

        chains = []
        for ring in range(params.rings):
            if ring > 0:
                ringRadius = ring * params.radius * 2.0
                ringCircumfrence = 2.0 * pi * ringRadius
                spiralCount = int(ringCircumfrence / (2.0 * params.radius))
                anglePerSpiral = 360.0 / spiralCount
                angleEnd = 45.0 + anglePerSpiral
            else:
                ringRadius = 0.
                spiralCount = 1
                anglePerSpiral = 0.
                angleEnd = 0.

            for spiral in range(spiralCount):
                xC = params.xCenter + cos(radians(spiral*anglePerSpiral)) * ringRadius
                yC = params.yCenter + sin(radians(spiral*anglePerSpiral)) * ringRadius
                aE = 0 if spiral == spiralCount-1 else angleEnd + 360. * spiral / spiralCount
                chains.append(Chains.spiral(xC, yC, 0., params.radius*params.factor, params.turns, angleRate=params.angleRate, angleEnd=aE))
        return chains
