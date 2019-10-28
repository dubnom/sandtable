from dialog import DialogList, DialogInt
from random import randint
from palettes import palettes
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        pal = list(palettes.keys())[randint(0, len(palettes)-1)]
        self.editor = [
            DialogList("palette",      "Palette",                      default=pal, list=sorted(palettes.keys())),
            DialogInt("points",       "Points per Color",             default=5, min=1, max=200),
            DialogInt("steps",        "Points to Step",               default=5, min=1, max=200),
            DialogInt("delaySteps",   "Delay Steps",                  default=20, min=0, max=1000),
        ]

    def generator(self, leds, params):
        colors = palettes[params.palette](params).getColors() if params.palette in palettes else [(0, 0, 0)]
        end = leds.count
        shift = 0
        while True:
            c, light = 0, 0
            for led in range(end):
                leds.set((shift+led) % end, colors[c])
                light = (light + 1) % params.points
                if light == 0:
                    c = (c + 1) % len(colors)
            yield True

            for delay in range(params.delaySteps):
                yield False

            shift = (shift + params.steps) % end
