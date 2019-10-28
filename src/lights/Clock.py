from time import localtime, time
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.shift = cols / 2
        self.editor = []

    def generator(self, leds, params):
        end = leds.count
        colors = [(255, 255, 0), (255, 0, 255), (0, 255, 255), (0, 0, 255)]
        mults = [end/12.0, end/60.0, end/60.0, end]

        oldtm = None
        while True:
            t = localtime()
            tm = (t.tm_hour % 12, t.tm_min, t.tm_sec, time() % 1.0)
            if tm == oldtm:
                yield False
            else:
                leds.clear()
                for color, mult, v in zip(colors, mults, tm):
                    leds.set(int(self.shift + mult * v) % end, color)
                oldtm = tm
                yield True
