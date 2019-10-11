from random import randint
from Sand import *
from dialog import *

class Pastel( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = []

    def generator( self, leds, cols, rows, params ):
        end = cols * 2 + rows * 2
        ends = [ 0 ] * end
        for led in range( 0, end ):
            leds.set( led, self._randomRGB())
            ends[ led ] = self._randomRGB()
        
        while True:
            for led in range( 0, end ):
                if leds.get( led ) == ends[ led ]:
                    ends[ led ] = self._randomRGB()
                else:
                    (r1,g1,b1) = leds.get( led )
                    (r2,g2,b2) = ends[ led ]
                    r1 += cmp(r2,r1)
                    g1 += cmp(g2,g1)
                    b1 += cmp(b2,b1)
                    leds.set( led, (r1, g1, b1 ))
            yield True
    
    def _randomRGB( self ):
        return (randint(0,255), randint(0,255), randint(0,255))
