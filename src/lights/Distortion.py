from dialog import DialogInt
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogInt("steps",           "Transition Steps",         default=20, min=3, max=200),
        ]

    def generator(self, leds, params):
        # Setup the groups
        self.groups = [
            leds.rectangle[0] + leds.rectangle[2],  # Top and bottom
            leds.rectangle[1] + leds.rectangle[3]   # Right and left
        ]

        # Setup the brightness table
        brightness = [None] * params.steps
        for step in range(params.steps):
            level = int(step * 255. / params.steps)
            brightness[step] = (level, level, level)

        # Alternate ramping up and down the brightness of the rows and columns
        groupNumber = 0
        while True:
            for step in range(params.steps):
                bright = brightness[step]
                list(map(lambda led: leds.set(led, bright), self.groups[groupNumber]))
                bright = brightness[params.steps - step - 1]
                list(map(lambda led: leds.set(led, bright), self.groups[1-groupNumber]))
                yield True
            groupNumber = 1 - groupNumber
