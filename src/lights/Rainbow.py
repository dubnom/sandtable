from math import fmod
from dialog import DialogFloat, DialogInt, DialogBreak
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogFloat("degsPerFrame",    "Degrees per refresh",      units="degrees", default=2., min=-60., max=60., step=1.),
            DialogFloat("degsSpan",        "Color span",               units="degrees", default=0.5, min=0.001, max=360., step=.5),
            DialogInt("delaySteps",      "Delay steps",              default=0, min=0, max=500),
            DialogBreak(),
            DialogInt("brightness",      "Brightness",               units="percent", default=50, min=0, max=100),
        ]

    def generator(self, leds, params):
        degree = 0.0
        while True:
            for led in range(0, leds.count):
                leds.set(led, leds.HSB(led / params.degsSpan + degree, 100, params.brightness))
            yield True
            for delay in range(params.delaySteps):
                yield False
            degree = fmod(degree + params.degsPerFrame, 360.0)
