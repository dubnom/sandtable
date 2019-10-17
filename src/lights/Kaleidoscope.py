from random import randint
from Sand import *
from dialog import *

class Lighter( Ledable ):
    steps = 15

    def __init__( self, cols, rows ):
        self.editor = []

    def generator( self, leds, cols, rows, params ):
        ucl, ucr, lcr, lcl = 0, cols-1, cols+rows-1, cols*2+rows-1
        url, urr, lrr, lrl = cols*2+rows*2-1, cols, cols+rows-1, cols*2+rows
        self.lights = [ [ucl+col, ucr-col, lcr+col, lcl-col] for col in range( 0, col//2 )] \
                + [ [urr+row, lrr-row, lrl+row, url-row] for row in range( 0, rows//2 )] 
        count = len( self.lights )
        colors = [ None ] * count
        newColors = [ None ] * count
        for c in range( count ):
            colors[ c ] = leds.RGBRandomBetter()
        
        while True:
            for step in range( self.steps ):
                ratio = float( step ) / self.steps
                for c in range( count ):
                    rgb = leds.RGBBlend( colors[ c ], colors[ c - 1 ], ratio )
                    for led in self.lights[ c ]:
                        leds.set( led, rgb )
                yield True
            # Shift
            colors.pop( 0 )
            colors.append( leds.RGBRandomBetter())
