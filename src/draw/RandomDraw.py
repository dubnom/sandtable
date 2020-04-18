import random
from Sand import TABLE_UNITS, MACHINE_UNITS, MACHINE_FEED, MACHINE_ACCEL, drawers
from sandable import Sandable, sandableFactory
from Chains import Chains
from dialog import DialogInt, DialogBreak, DialogFloat, Params


class Sander(Sandable):
    """
### Draw a random pattern
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        self.ballSize = ballSize
        self.units = units

        self.editor = [
            DialogInt("seed",        "Random seed",              default=random.randint(0, 10000000), min=0, max=10000000, rbutton=True),
            DialogBreak(),
            DialogFloat("drawTimeMin", "Minimum draw time",        units="minutes", default=0.5, min=0.5),
            DialogFloat("drawTimeMax", "Maximum draw time",        units="minutes", default=30.0, min=10.0),
        ]

    def generate(self, params):
        if not params.seed or params.drawTimeMax - params.drawTimeMin < 5.0:
            return []
        boundingBox = [(0.0, 0.0), (self.width, self.length)]
        random.seed(params.seed)
        while True:
            sandable = drawers[random.randint(0, len(drawers)-1)]
            sand = sandableFactory(sandable, self.width, self.length, self.ballSize, self.units)
            p = Params(sand.editor)
            p.randomize(sand.editor)
            chains = sand.generate(p)
            pchains = Chains.bound(chains, boundingBox)
            pchains = Chains.convertUnits(chains, TABLE_UNITS, MACHINE_UNITS)
            t, d, p = Chains.estimateMachiningTime(pchains, MACHINE_FEED, MACHINE_ACCEL)
            if params.drawTimeMin <= t/60.0 <= params.drawTimeMax:
                return chains
