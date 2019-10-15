from Sand import *
from Chains import *
from dialog import *
from random import randint

class RandomDraw( Sandable ):
    """
### Draw a random pattern
"""

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "seed",        "Random seed",              default = randint(0,10000000), min = 0, max = 10000000, rbutton = True ),
            DialogBreak(),
            DialogFloat( "drawTimeMin", "Minimum draw time",        units = "minutes", default = 0.5, min = 0.5 ),
            DialogFloat( "drawTimeMax", "Maximum draw time",        units = "minutes", default = 30.0, min = 10.0 ),
        ]

    def generate( self, params ):
        if not params.seed or params.drawTimeMax - params.drawTimeMin < 5.0:
            return []
        boundingBox = [ (0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH) ]
        random.seed( params.seed )
        while True:
            sandable = sandables[ random.randint(0,len(sandables)-1) ]
            sand = sandableFactory( sandable )
            p = Params( sand.editor )
            p.randomize( sand.editor )
            chains = sand.generate( p )
            t, d, p = Chains.estimateMachiningTime( chains, boundingBox, TABLE_FEED, TABLE_ACCEL )
            if params.drawTimeMin <= t/60.0 <= params.drawTimeMax:
                return chains 
