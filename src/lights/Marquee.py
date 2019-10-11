from Sand import *
from dialog import *

class Marquee( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = [
            DialogInt(  "modulus",      "Lights per Marquee",       default = 10, min = 1, max = 1000 ),
            DialogInt(  "delaySteps",   "Delay Steps",              default = 10, min = 0, max = 1000 ),
        ]

    def generator( self, leds, cols, rows, params ):
        end = (cols + rows) * 2
        shift = 0
        angle = 360 / params.modulus
        colors = [ None ] * params.modulus
        while True:
            for degree in range( 0, 360, 1 ):
                colors = [ leds.HSB( degree + colorNum * angle, 100, 50 ) for colorNum in range( 0, params.modulus )]
                for led in range( 0, end ):
                    leds.set( led, colors[ (led + shift) % params.modulus ] )
                shift = (shift + 1) % params.modulus
                yield True
                for delay in range( params.delaySteps ):
                    yield False


