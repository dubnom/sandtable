from dialog import DialogColor
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogColor("color",           "Color",                default=(255, 0, 0)),
        ]

    def generator(self, leds, params):
        leds.set(0, params.color, leds.count - 1)
        yield True
        while True:
            yield False
