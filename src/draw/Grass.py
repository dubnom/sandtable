from sandable import Sandable, inchesToUnits
from dialog import DialogFloat, DialogInt, DialogYesNo
from Chains import Chains
import random


class Sander(Sandable):
    """
### Draw fields of grass

#### Parameters

* **Maximum height** - height of the tallest blade of grass.
* **Maximum wind** - simulate wind to move the blades around.
* **Blades of grass** - number of blades to draw.
* **Directional wind** - if "yes" then the wind comes only from one direction.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("maxHeight",       "Maximum height",       units=units, default=length * .75, min=1.0, max=length),
            DialogFloat("maxWind",         "Maximum wind",         units=units, default=inchesToUnits(1., units), min=0., max=inchesToUnits(4., units)),
            DialogInt("blades",          "Blades of grass",      default=100, min=1, max=250),
            DialogYesNo("dWind",           "Directional wind",),
        ]
        self.width = width
        self.length = length
        self.thickness = inchesToUnits(1, units)
        self.steps = 5

    def generate(self, params):
        chains = []
        directionalWind = random.uniform(-params.maxWind, params.maxWind)
        for blade in range(params.blades):
            chain1 = []
            chain2 = []
            x = random.random() * self.width
            mh = random.random() * params.maxHeight
            if params.dWind:
                w = random.random() * directionalWind
            else:
                w = random.uniform(-params.maxWind, params.maxWind)
            h = 0
            thickness = self.thickness
            for step in range(self.steps):
                chain1.append((x, h))
                chain2.append((x+thickness, h))
                h += mh / self.steps
                x += w
                w *= 1.5
                thickness *= (1.0 - 1./self.steps)
            chain2.reverse()
            chains.append(Chains.Spline(chain1))
            chains.append(Chains.Spline(chain2))
        return chains
