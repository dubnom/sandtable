from Sand import *
from dialog import *
from Chains import *
import random

class Grass( Sandable ):
    """
        <h3>Draw fields of grass</h3>"""
    
    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "maxHeight",       "Maximum height",       units = "inches", default = length * .75, min = 1.0, max=length ),
            DialogFloat( "maxWind",         "Maximum wind",         units = "inches", default = 1., min=0., max = 4. ),
            DialogInt(   "blades",          "Blades of grass",      default = 100, min = 1, max = 250 ),
            DialogYesNo( "dWind",           "Directional wind",     ),
        ]
        self.width  = width
        self.length = length

    def generate( self, params ):
        chains = []
        directionalWind = random.uniform( -params.maxWind, params.maxWind )
        for blade in range(params.blades):
            chain1 = []
            chain2 = []
            x = random.random() * self.width
            mh = random.random() * params.maxHeight
            if params.dWind:
                w = random.random() * directionalWind
            else:
                w = random.uniform( -params.maxWind, params.maxWind )
            thickness = 1.
            steps = 5
            h = 0
            for step in range(steps):
                chain1.append( (x,h) )
                chain2.append( (x+thickness,h) )
                h += mh/steps
                x += w
                w *= 1.5
                thickness *= (1.0 - 1./steps) 
            chain2.reverse()
            chains.append( Chains.Spline( chain1 ))
            chains.append( Chains.Spline( chain2 ))
        return chains