from math import e
from dialog import DialogInt
from palettes import palettes
from ledable import Ledable


class Gauss:
    """Gaussian function used to feather the lighting."""

    def __init__(self, maxHeight, center, stdDev):
        self.maxHeight = maxHeight
        self.center = center
        self.stdDev = stdDev

    def value(self, x):
        return self.maxHeight * pow(e, -(((x-self.center)**2) / (2.*self.stdDev**2)))


class Lighter(Ledable):
    """Create a light simulation of a sky that goes from sunrise to sunset."""

    def __init__(self, cols, rows):
        self.editor = [
            DialogInt("whatever",     "Variable",         units="McValues"),
        ]

    def generator(self, leds, cols, rows, params):
        # Sunrise starts with a black sky
        # The light slowly starts to brighten from the east
        # With the centerpoint slowly arching to the north or south (parameter)
        # The colors follow the sunrise/sunset palette

        # Daylight goes through hues of blue
        # clouds drift slowly across (lower intensity grey spectrum)

        # Sunset is reverse of sunrise

        # FIX: To start, generate a simple static sunrise
        count = 2 * (rows + cols)
        pal = palettes['Sunset'](params).getColors()
        pal.reverse()
        g = Gauss(len(pal)-1, count / 2.0, count / 15.)
        for led in range(0, count):
            v = pal[int(round(g.value(led)))]
            leds.set(led, v)
        yield True
        while True:
            yield False
