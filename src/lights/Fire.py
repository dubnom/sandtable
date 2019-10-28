from random import randint
from dialog import DialogList, DialogInt
from palettes import palettes
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.end = cols * 2 + rows * 2
        self.editor = [
            DialogList("palette",  "Palette",              default='Fire', list=sorted(palettes.keys())),
            DialogInt("speed",    "Ember Delay",          default=10, min=1, max=30),
            DialogInt("b",        "Brightness",           default=128, min=1, max=255),
        ]

    def generator(self, leds, params):
        self.colors = palettes[params.palette](params).getColors() if params.palette in palettes else [(0, 0, 0)]
        self.speed = params.speed
        self.brightness = params.b / 255.0

        myLeds = [self._newLed() for led in range(self.end)]
        while True:
            for led in range(self.end):
                leds.set(led, tuple(int(c) for c in myLeds[led][0]))
                if myLeds[led][2]:
                    newColor = tuple(s+i for s, i in zip(myLeds[led][0], myLeds[led][1]))
                    myLeds[led][0] = newColor
                    myLeds[led][2] -= 1
                else:
                    myLeds[led] = self._newLed()
            yield True

    def _newLed(self):
        startRGB, endRGB = self._randomRGB(), self._randomRGB()
        speed = randint(self.speed, 5*self.speed)
        incs = tuple((e - s) / speed for s, e in zip(startRGB, endRGB))
        return [startRGB, incs, speed]

    def _randomRGB(self):
        return [c*self.brightness for c in self.colors[randint(0, len(self.colors)-1)]]
