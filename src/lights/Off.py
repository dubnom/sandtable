import colorsys
from Sand import LED_PERIOD
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = []

    def generator(self, leds, params):
        # Slowly dim down the brightness (v) of any led that is on.
        # This is done by getting all of the initial HSV values and subtracting a small value every iteration
        #
        hsvs = [colorsys.rgb_to_hsv(led[0]/255.0, led[1]/255.0, led[2]/255.0) for led in leds.leds]
        while True:
            maxv = 0.0
            for i, (h, s, v) in enumerate(hsvs):
                v = max(0.0, v - .08)
                hsvs[i] = (h, s, v)
                rgb = colorsys.hsv_to_rgb(h, s, v)
                leds.set(i, (int(rgb[0]*255.0), int(rgb[1]*255.0), int(rgb[2]*255.0)))
                maxv = max(maxv, v)
            yield True
            if maxv == 0.0:
                break
        # Send off signals for a second in case the leds are lagging
        leds.clear()
        for i in range(int(1.0 / LED_PERIOD)):
            yield True
