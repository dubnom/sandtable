from LedsBase import LedsBase
from random import randint

palettes = {
    "Random": lambda p: PaletteRandom(p),
    "Rainbow": lambda p: PaletteRainbow(p),
    "Hue": lambda p: PaletteHue(p),
    "Chanukah": lambda p: PaletteStatic(p, [(0, 0, 255), (255, 255, 255)]),
    "Christmas": lambda p: PaletteStatic(p, [(255, 0, 0), (0, 255, 0)]),
    "Kwanza": lambda p: PaletteStatic(p, [(0, 255, 0), (255, 0, 0), (0, 0, 0)]),
    "Halloween": lambda p: PaletteStatic(p, [(241, 88, 2), (0, 0, 0)]),
    "Indendence Day": lambda p: PaletteStatic(p, [(224, 22, 43), (255, 255, 255), (0, 82, 165)]),
    "Thanksgiving": lambda p: PaletteStatic(p, [(53, 5, 4), (162, 26, 0), (245, 111, 21), (252, 181, 33), (255, 232, 112)]),
    "Valentine's Day": lambda p: PaletteStatic(p, [(130, 0, 129), (254, 89, 194), (254, 64, 185), (254, 28, 172), (57, 0, 57)]),
    "St. Patrick's Day": lambda p: PaletteStatic(p, [(60, 191, 27), (17, 59, 12), (48, 120, 48), (191, 211, 0), (49, 88, 17)]),
    "Chinese New Year": lambda p: PaletteStatic(p, [(77, 108, 49), (112, 153, 77), (246, 235, 93), (254, 185, 84), (247, 72, 77)]),
    # "Fire":             lambda p: PaletteStatic( p, [(19,0,28), (171,0,11), (222,74,0), (255,136,0), (255,247,0)] ),
    "Fire": lambda p: PaletteStatic(p, [(255, 0, 0), (128, 0, 0), (255, 90, 0), (128, 45, 0), (128, 77, 0), (128, 103, 0), (255, 232, 8),
                                        (15, 15, 0), (0, 0, 0), (0, 0, 0)]),
    "Traffic Light": lambda p: PaletteStatic(p, [(0, 142, 9), (255, 191, 0), (255, 3, 3)]),
    "Sunset": lambda p: PaletteStatic(p, [(240, 78, 78), (236, 99, 52), (229, 142, 34), (94, 42, 118), (84, 20, 88)]),
    "Ocean": lambda p: PaletteStatic(p, [(0, 20, 73), (1, 38, 119), (0, 91, 197), (0, 180, 252), (23, 249, 255)]),
}


class Palette:
    def __init__(self, params):
        self.params = params
        pass

    def getColors(self, limit=0):
        pass


class PaletteStatic(Palette):
    def __init__(self, params, pal):
        self.params = params
        self._pal = pal

    def getColors(self, limit=0):
        return self._pal

    def getRandom(self, count=5):
        size = len(self._pal)-1
        return [self._pal[randint(0, size)] for c in range(count)]


class PaletteRandom(Palette):
    def __init__(self, params):
        # FIX: Use parameters
        pass

    def getColors(self, limit=5):
        return self.getRandom(limit)

    def getRandom(self, count=5):
        return [LedsBase.RGBRandomBetter() for c in range(count)]


class PaletteRainbow(Palette):
    def __init__(self, params):
        # FIX: Use parameters
        pass

    def getColors(self, limit=7):
        angle = 360. / limit
        return [LedsBase.HSB(angle*c, 100, 50) for c in range(limit)]

    def getRandom(self, count=5):
        return [LedsBase.HSB(randint(0, 359), 100, 50) for c in range(count)]


class PaletteHue(Palette):
    def __init__(self, params):
        try:
            self.hue, b, s = LedsBase.RGBtoHSB(params.color)
        except (TypeError, AttributeError):
            self.hue = randint(0, 359)

    def getColors(self, limit=7):
        divs = 100. / limit
        return [LedsBase.HSB(self.hue, c*divs, 50) for c in range(limit)]

    def getRandom(self, count=5):
        return [LedsBase.HSB(self.hue, randint(0, 100), 50) for c in range(count)]
