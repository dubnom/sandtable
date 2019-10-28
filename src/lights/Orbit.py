from dialog import DialogColor
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogColor("color",           "Color",                default=(128, 128, 128)),
        ]

    def generator(self, leds, params):
        on = params.color
        off = (0, 0, 0)
        while True:
            for led in range(leds.count):
                leds.set(led, on)
                yield True
                leds.set(led, off)
