from Sand import *
from dialog import *

class Lighter( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = [
            DialogColor( "color",           "Color",                default=(255,0,0) ),
        ]
    
    def generator( self, leds, cols, rows, params ):
        end = (cols + rows) * 2 - 1
        leds.set( 0, params.color, end )
        yield True
        while True:
            yield False

