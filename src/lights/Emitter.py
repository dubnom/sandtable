from math import fmod
from Sand import *
from dialog import *

class Emitter( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = [
            DialogFloat( "angle",           "Source angle",         units = "degrees", default = 2.0, min = 0.0, max = 720.0, step = 1. ),
            DialogFloat( "degsPerFrame",    "Degrees per refresh",  units = "degrees", default = 2.0, min = 0.0, max = 30.0, step = 1. ),
            DialogFloat( "degsSpan",        "Color span",           units = "degrees", default = 0.5, min = 0.00001, max = 360.0, step = .5 ),
            DialogInt(   "delaySteps",      "Delay steps",          default = 0, min = 0, max = 500 ),
            DialogBreak(),
            DialogInt(   "brightness",      "Brightness",           units = "percent", default = 50, min = 0, max = 100 ),
        ]

    def generator( self, leds, cols, rows, params ):
        end = (cols + rows) * 2
        emitter = int(end * params.angle / 360.) % 360
        degree = 0.
        while True:
            for offset in range(end/2):
                leds.set( (emitter + offset) % end, leds.HSB( offset + degree, 100, params.brightness ))
                leds.set( (emitter - offset) % end, leds.HSB( offset + degree, 100, params.brightness ))
            yield True
            for delay in range( params.delaySteps ):
                yield False
            degree = fmod( degree + params.degsPerFrame, 360.0 ) 
