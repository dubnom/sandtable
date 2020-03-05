import board
import adafruit_dotstar as dotstar
from LedsBase import LedsBase


class Leds(LedsBase):
    """Communicate with a DotStar lighting system"""

    def __init__(self, rows, cols, mapping, params):
        self.mapping = mapping
        self.params = params
        LedsBase.__init__(self, rows, cols)

    def connect(self):
        brightness = self.params.get( 'brightness', 1. ) if self.params else 1. 
        self.strip = dotstar.DotStar(board.SCK, board.MOSI, self.count, auto_write=False)

    def refresh(self):
        for led, color in enumerate(self.leds):
            if self.mapping:
                color = self.leds[self.mapping[led]]
            self.strip[led] = (int(color[0]), int(color[1]), int(color[2]))
        self.strip.show()

    def disconnect(self):
        del self.strip
