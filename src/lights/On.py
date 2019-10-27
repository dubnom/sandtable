from Sand import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = []

    def generator(self, leds, cols, rows, params):
        for n in range(0, 256, 5):
            leds.set(0, (n, n, n), end=leds.count-1)
            yield True
        while True:
            yield False
