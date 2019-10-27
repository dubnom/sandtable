from Sand import Ledable
from dialog import DialogColor


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogColor("color",           "Color",                default=(128, 128, 128)),
        ]

    def generator(self, leds, cols, rows, params):
        end = (cols + rows) * 2
        on = params.color
        off = (0, 0, 0)
        while True:
            for led in range(end):
                leds.set(led, on)
                yield True
                leds.set(led, off)
