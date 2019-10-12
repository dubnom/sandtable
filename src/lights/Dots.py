from Sand import *
from dialog import *
from palettes import *

class Dots( Ledable ):
    def __init__( self, cols, rows ):
        pal = list(palettes.keys())[ randint(0,len(palettes)-1) ]        
        self.editor = [
            DialogList( "palette",      "Palette",                      default = pal, list = sorted( palettes.keys()) ),
            DialogInt(  "dots",         "Number of Dots",               default = 20, min = 1, max = (cols + rows) * 2, ),
        ]

    def generator( self, leds, cols, rows, params ):
        end = leds.count
        colors = palettes[ params.palette ]( params ).getRandom(params.dots) if params.palette in palettes else [ (0,0,0) ]
        dots = [ [random.randint(0,end), (random.random()-.5)*3.0, color] for color in colors ]

        while True:
            leds.clear()
            for dot in dots:
                dot[0] += dot[1]
                leds.set( int(dot[0]) % end, dot[2] )
            yield True
