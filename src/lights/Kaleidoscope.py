from ledable import Ledable


class Lighter(Ledable):
    steps = 15

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.ucl, self.ucr, self.lcr, self.lcl = 0, cols-1, cols+rows-1, cols*2+rows-1
        self.url, self.urr, self.lrr, self.lrl = cols*2+rows*2-1, cols, cols+rows-1, cols*2+rows
        self.editor = []

    def generator(self, leds, params):
        self.lights = [[self.ucl+col, self.ucr-col, self.lcr+col, self.lcl-col] for col in range(0, self.cols//2)] \
            + [[self.urr+row, self.lrr-row, self.lrl+row, self.url-row] for row in range(0, self.rows//2)]
        count = len(self.lights)
        colors = [None] * count
        for c in range(count):
            colors[c] = leds.RGBRandomBetter()

        while True:
            for step in range(self.steps):
                ratio = float(step) / self.steps
                for c in range(count):
                    rgb = leds.RGBBlend(colors[c], colors[c - 1], ratio)
                    for led in self.lights[c]:
                        leds.set(led, rgb)
                yield True
            # Shift
            colors.pop(0)
            colors.append(leds.RGBRandomBetter())
