from Sand import LED_PERIOD
from dialog import DialogInt
from ledable import Ledable


class Lighter(Ledable):
    brightnesses = [1.0, 0.9, 0.1, 0.2, 0.3, 0.5, 0.3, 0.4, 0.2, 0.3]

    def __init__(self, cols, rows):
        self.end = (cols + rows) * 2 - 1
        self.editor = [
            DialogInt("rate",           "Heart Rate",            default=70, min=25, max=200),
        ]

    def generator(self, leds, params):
        steps = int((60.0 / LED_PERIOD) / (params.rate * len(self.brightnesses)))
        while True:
            for i in range(len(self.brightnesses)):
                base = self.brightnesses[i-1]
                slope = (self.brightnesses[i] - base) / steps
                for step in range(steps):
                    color = (int(255 * (base + slope * step)), 0, 0)
                    leds.set(0, color, self.end)
                    yield True
