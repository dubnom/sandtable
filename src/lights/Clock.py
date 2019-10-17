from Sand import *
from dialog import *
from time import localtime, time

class Lighter( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = []

    def generator( self, leds, cols, rows, params ):
        end = leds.count
        colors = [ (255,255,0), (255,0,255), (0,255,255), (0,0,255) ]
        mults  = [ end/12.0, end/60.0, end/60.0, end ]
        shift  = cols / 2

        oldtm = None
        while True:
            t = localtime()
            tm = (t.tm_hour % 12, t.tm_min, t.tm_sec, time() % 1.0 )
            if tm == oldtm:
                yield False
            else:
                leds.clear()
                for color,mult,v in zip( colors, mults, tm ):
                    leds.set( int( shift + mult * v ) % end, color )
                oldtm = tm
                yield True

