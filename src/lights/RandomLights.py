from random import randint
from dialog import DialogFloat, Params
from time import time
from ledable import Ledable, ledPatternFactory
from Sand import ledPatterns


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogFloat("minutes",      "Light Pattern Change Frequency",   units="minutes", default=1.0, min=0.25, max=10.0),
        ]
        self.patterns = [c for c in ledPatterns if c not in ['Random', 'Off']]

    def generator(self, leds, cols, rows, params):
        while True:
            pattern = self.patterns[randint(0, len(self.patterns)-1)]
            pat = ledPatternFactory(pattern, cols, rows)

            iParams = Params(pat.editor)
            iParams.randomize(pat.editor)
            gen = pat.generator(leds, cols, rows, iParams)
            endTime = time() + params.minutes * 60.0
            try:
                while time() < endTime:
                    yield next(gen)
            except StopIteration:
                pass
