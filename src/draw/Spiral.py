from dialog import DialogFloat, DialogYesNo, DialogBreak
from Chains import Chains
from sandable import Sandable, SandException


class Sander(Sandable):
    """
### Simple figures that create a surprisingly large number of beautiful paterns

#### Hints

Try playing with **Sample rate** first.

#### Parameters

* **First radius** and **Second radius** - how far from the center the spiral should start and end.
* **Turns** - number of lines drawn within the spiral.
* **Starting angle** - the angle the spiral starts at. The default of 0.0 starts to the right of center.
* **Sample rate** - how frequently points are calculated around the spiral.  Smaller numbers create rounder
  spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
  121 to get a rotating triangle; 74 makes a rotating pentagon.
* **Growth base power** - how quickly the outer rings of the spiral get farther from each other.
  The default of 1.0 creates a linear spiral, try 2.0 or more for a spiral that grows faster
  and 0.5 for a spiral that is big in the center.
* **Fill in spiral** - draw lines between points of each subsequent spiral arm.
  This creates a full filled-in spiral that looks pretty neat in sand.
* **Fit to table** - Warp the circular shape to the dimensions of the table.
* **X Center** and **Y Center** - where the center of the spiral will be relative to the table.
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.editor = [
            DialogFloat("r1",              "First radius",         units=units, min=0.0, max=max(width, length)*2),
            DialogFloat("r2",              "Second radius",        units=units,  default=min(width, length)/2, min=0.0, max=max(width, length)*2),
            DialogFloat("turns",           "Turns",                default=10., min=0.1, max=100.),
            DialogFloat("angleStart",      "Starting angle",       units="degrees", min=0.0, max=360.0, step=15.),
            DialogFloat("angleRate",       "Sample rate",          units="degrees", default=15.0, min=-180.0, max=180.0),
            DialogFloat("base",            "Growth base power",    default=1.0, min=0.25, max=10.0),
            DialogYesNo("fill",            "Fill in spiral"),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
        ]

    def generate(self, params):
        if not params.angleRate:
            raise SandException("Sample Rate cannot be zero")

        xC, yC = params.xCenter, params.yCenter
        chain = Chains.spiral(xC, yC, params.r1, params.r2, params.turns, params.angleRate, params.angleStart, params.base, params.fill)

        if params.fitToTable:
            chain = Chains.circleToTable(chain, self.width, self.length)
        return [chain]
