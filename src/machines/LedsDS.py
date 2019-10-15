from dotstar import Adafruit_DotStar
from LedsBase import LedsBase

class Leds(LedsBase):
    """Communicate with a DotStar lighting system"""
    def __init__( self, rows, cols, mapping, params ):
        self.mapping = mapping
        LedsBase.__init__(self,rows,cols)

    def connect( self ):
        self.strip = Adafruit_DotStar(self.count)
        self.strip.begin()

    def refresh( self ):
        for led,color in enumerate(self.leds):
            if self.mapping:
                color = self.leds[self.mapping[led]]
            # Note: GRB is used!
            self.strip.setPixelColor(led, int(color[0])<<8 | int(color[1])<<16 | int(color[2]))
        self.strip.show()

    def disconnect( self ):
        del self.strip
