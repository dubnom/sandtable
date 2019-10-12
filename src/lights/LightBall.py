from Sand import *
from dialog import *
import mach

class LightBall( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = []

    def generator( self, leds, cols, rows, params ):
        lights = [
                (-3, (64,64,64)),
                (-2, (128,128,128)),
                (-1, (192,192,192)),
                (0,  (255,255,255)),
                (1,  (192,192,192)),
                (2,  (128,128,128)),
                (3,  (64,64,64))]

        # Number of leds off the drawing surface (bottom left, top right)
        xOffset = LED_OFFSETS[0][0]
        xSlope  = (LED_COLUMNS - LED_OFFSETS[0][0] - LED_OFFSETS[1][0]) / TABLE_WIDTH
        yOffset = LED_OFFSETS[0][1]
        ySlope  = (LED_ROWS - LED_OFFSETS[0][1] - LED_OFFSETS[1][1]) / TABLE_LENGTH

        with mach.mach() as e:
            oldX, oldY = -1, -1
            while True:
                # Poll EMC for the location
                x, y = e.getPosition()
                if x != oldX or y != oldY:
                    col = min( int( xOffset + x * xSlope), LED_COLUMNS)
                    row = min( int( yOffset + y * ySlope), LED_ROWS)
                    leds.clear()
                    for offset,color in lights:
                        c = col + offset
                        if c >= 0 and c < LED_COLUMNS:
                            leds.set( c, color )
                            leds.set( LED_ROWS + 2 * LED_COLUMNS - c - 1, color )
                        r = row + offset
                        if r >= 0 and r < LED_ROWS:
                            leds.set( LED_COLUMNS + LED_ROWS - r - 1, color )
                            leds.set( 2 * LED_COLUMNS + LED_ROWS + r, color )
                    oldX, oldY = x, y
                    yield True
                else:
                    yield False
