import board
import neopixel
from LedsBase import LedsBase


class Leds(LedsBase):
    """Communicate with a DotStar lighting system"""

    def __init__(self, rows, cols, mapping, params):
        self.mapping = mapping
        LedsBase.__init__(self, rows, cols)

    def connect(self):
        self.strip = neopixel.NeoPixel(board.D18, self.count, auto_write=False )

    def refresh(self):
        for led, color in enumerate(self.leds):
            if self.mapping:
                color = self.leds[self.mapping[led]]
            self.strip[led] = (int(color[0]), int(color[1]), int(color[2]))
        self.strip.show()

    def disconnect(self):
        del self.strip

