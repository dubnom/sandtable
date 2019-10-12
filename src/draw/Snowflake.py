from builtins import range
from math import sqrt, radians, sin, cos
import random
from Sand import *
from dialog import *
from Chains import * 
    
class Snowflake( Sandable ):
    """
        <h3>Draw something that looks like a snowflake</h3>

        <ul>
         <li><i>Depth of fractility</i> - the number of times the snowflake should try to branch.
         <li><i>Probability of branching</i> - the probability of the snowflake actually branching when it tries.
         <li><i>Fractility size decrease</i> - how quickly each branch gets smaller than its parent.
         <li><i>Rounded crystals</i> - Round the edges or keep them straight.
        <li><i>Random seed</i> - this is used to generate random snowflakes.  Different seeds generate different patterns.
             The <i>Random</i> button will create new seeds automatically.
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the spiral will be relative to the table.
        </ul>

        Some parameters that make pretty snowflakes:
        <blockquote>
         <table>
          <tr><th>Description</th><th>Parameters</th></tr>
          <tr><td>Snowflake 1</td><td>3, 0.4, 0.2, 6890</td></tr>
          <tr><td>Snowflake 2</td><td>3, 0.4, 0.2, 2077</td></tr>
          <tr><td>Snowflake 3</td><td>3, 0.4, 0.2, 5133</td></tr>
          <tr><td>Snowflake 4</td><td>3, 0.5, 0.1, 3737</td></tr>
         </table>
        </blockquote>"""

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "depth",               "Depth of fractility",      default = 2, max = 10 ),
            DialogFloat( "branchProbability",   "Probability of branching", default = 0.7, min = 0.0, max = 1.0 ),
            DialogFloat( "percent",             "Fractility size decrease", default = 0.3 ),
            DialogYesNo( "round",               "Rounded crystals",         default = False ),
            DialogInt(   "seed",                "Random seed",              default = 1, min = 0, max = 10000, rbutton = True ),
            DialogBreak(),
            DialogFloat( "xCenter",             "X Center",                 units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",             "Y Center",                 units = "inches", default = length / 2.0 ),
        ]
        self.table = [(0.0,0.0),(width,length)]


    def generate( self, params ):
        random.seed( params.seed )
        
        chain = [ (0.0, 0.0), (1.0, 0.0) ]

        point0 = None 
        for depth in range( params.depth ):
            newChain = []
            for point1 in chain:
                if not point0:
                    point0 = point1
                    newChain.append( point1 )
                elif random.random() < params.branchProbability:
                    length = sqrt( (point1[0] - point0[0]) ** 2.0 + (point1[1] - point0[1]) ** 2.0 ) * params.percent
                    midpoint = (point0[0] + (point1[0] - point0[0]) / 2.0, point0[1] + (point1[1] - point0[1]) / 2.0)
                    polyCenter = (midpoint[0] + random.random() * length, midpoint[1] + random.random() * length)
                    newChain += self._makePolygon( midpoint, polyCenter, int( 3.0 + random.random() * 6.0 ))
                else:
                    newChain.append( point1 )
            chain = newChain

        # Mirror and rotate the chain 6 times
        backwards = chain[:]
        backwards.reverse()
        chain += [ (p[0], -p[1]) for p in backwards ]
        
        chains = []
        for angle in range( 0, 360, 60 ):
            chains += Chains.transform( Chains.rotate( [chain], angle ), (params.xCenter, params.yCenter ))
        if params.round:
            chains = Chains.splines( chains )
        return Chains.autoScaleCenter( chains, self.table )

    def _makePolygon( self, start, center, sides ):
        angle = 360.0 / sides
        chain = []
        for side in range(sides):
            s = sin( radians( angle * side))
            c = cos( radians( angle * side))
            x = start[0] - center[0]
            y = start[1] - center[1]
            chain.append( (center[0] + x * c - y * s, center[1] + (x * s + y * c)) )
        return chain

        
