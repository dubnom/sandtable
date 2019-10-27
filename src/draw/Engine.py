from math import sqrt
from sandable import Sandable
from dialog import DialogInt, DialogFloat, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### Engine-Turned patterns

#### Parameters

* **Rows** and **Columns** - number of rows and columns to create the engine-turned pattern with.
* **Turns** - number of lines drawn within a spiral.
  Changing this can make the lines closer together (try a number like 10) or farther apart (try 0.5).
* **Sample Rate** - how frequently points are calculated around the spiral.  Smaller numbers create rounder
  spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
  121 to get a rotating triangle; 74 makes a rotating pentagon.
* **Size Modifier** - smaller numbers decrease the size of the spiral, larger numbers increase the size.
* **X Corner** and **Y Corner** - lower left corner to start the pattern.
* **Width** and **Length** - size of the pattern (spirals can go outside of the bounds).
"""

    def __init__(self, width, length, ballSize, units):
        scale = width / length
        self.editor = [
            DialogInt("rows",            "Rows",                 default=8, min=1, max=20),
            DialogInt("cols",            "Columns",              default=int(8*scale), min=1, max=int(20*scale)),
            DialogFloat("turns",           "Turns",                default=3.0, min=1, max=15.0),
            DialogFloat("angleRate",       "Sample Rate",          units="degrees", default=15.0, min=-360.0, max=360.0),
            DialogFloat("sizeModifier",    "Size Modifier",        units="percent", default=1., min=.75, max=1.25),
            DialogBreak(),
            DialogFloat("xCorner",         "X Corner",             units=units, default=0.0, min=0.0, max=width, randRange=(0., 0.)),
            DialogFloat("yCorner",         "Y Corner",             units=units, default=0.0, min=0.0, max=length, randRange=(0., 0.)),
            DialogFloat("width",           "Width",                units=units, default=width, min=1.0, max=width, randRange=(width, width)),
            DialogFloat("length",          "Length",               units=units, default=length, min=1.0, max=length, randRange=(length, length)),
        ]

    def generate(self, params):
        if not params.angleRate:
            params.angleRate = 15.0

        radius = min(params.width / params.cols, params.length / params.rows) * sqrt(2.0) * .5 * params.sizeModifier
        rowSize, colSize = params.length / params.rows, params.width / params.cols
        rowHalf, colHalf = rowSize / 2, colSize / 2

        chains = []
        for row in range(params.rows):
            aE = 180 if row % 2 else 0
            for col in range(params.cols):
                rev = params.cols-col-1 if row % 2 else col
                xC = params.xCorner + rev * colSize + colHalf
                yC = params.yCorner + row * rowSize + rowHalf
                chain = Chains.spiral(xC, yC, 0, radius, params.turns, params.angleRate, angleEnd=aE)
                chains.append(chain)

        return chains
