from math import pi, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Spirograph( Sandable ):
    """
        <h3>Draw patterns similar to the Spirograph toy</h3>

        Hint: Simpler wheel teeth ratios produce simpler patterns. Prime numbers take a long time!<br>

        <p>A Spirograph is a geared toy where a gear wheel with a pen in it goes around (either inside or outside) another gear.
        This relatively simple arrangement is capable of drawing interesting geometric patterns. The SandTable takes this idea a
        bit further and allows an arbitrary number of gears to be used.</p>

        <ul>
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the drawing will be relative to the table.
             Usually not worth changing.
         <li><i>Radius</i> - how big the drawing should be. This shouldn't need changing but it is sometimes fun
             to pick larger numbers to zoom in.
         <li><i>Wheel Teeth</i> - a list of gears and their teeth.  The first number is a fixed gear, each subsequent
             gear orbits the previous gear. If the number of teeth is positive, the gear orbits on the outside, negative
             is on the inside.  Generally, the more wheels the more complex the image (and the longer it will take to generate).<br>
             <i>Wheel Teeth</i> is the parameter that is most interesting to change. Gear teeth can only be integers and
             they are separated in the list by commas.
         <li><i>Resolution</i> - how fine the curves are. Smaller numbers are more boxy while larger numbers make rounder curves.
        </ul>

        Some patterns to try:<p>

        <blockquote>
        <table>
         <tr><th>Description</th><th>Wheel Teeth</th><th>Resolution</th></tr>
         <tr><td>Clover</td><td>40,-30</td><td>7</td></tr>
         <tr><td>Inner Clover</td><td>40,30</td><td>9</td></tr>
         <tr><td>Detailed Triangle</td><td>100,-33</td><td>5</td></tr>
         <tr><td>Detailed 3-Lobes</td><td>100,33</td><td>5</td></tr>
         <tr><td>Prickly Cross</td><td>40,-30,-5</td><td>7</td></tr>
         <tr><td>Four Clouds</td><td>40,-30,5</td><td>7</td></tr>
         <tr><td>Sand Dollar</td><td>50,12,-4</td><td>7</td></tr>
        </table>
        </blockquote>"""

    MAX_POINTS = 25000

    def __init__( self, width, length ):
        self.editor = [
            DialogInts(  "teeths",          "Wheel Teeth",              units = "n1,n2,...", default=[40,-30], min=-60, max=60, minNums=2, maxNums=3 ),
            DialogInt(	 "resolution",      "Resolution",               default = 7, min = 1, max = 60 ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",                 units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",                 units = "inches", default = length / 2.0 ),
            DialogFloat( "radius",          "Radius",                   units = "inches", default = min(width,length)/2, min = 1.0 ),
        ]

    def generate( self, params ):
        # Get the number of teeth, renormalize based on common divisor, calculate radii
        teeth = params.teeths
        teeth = filter( lambda t: t, teeth )
        if len( teeth ) == 0:
            raise SandException( "There needs to be at least one number for Wheel Teeth" )

        teeth[0] = abs( teeth[0] )

        gcd = abs(self.gcdList( teeth ))
        teeth = [ tooth / gcd for tooth in teeth ]
        radii = [ tooth / (2.0 * pi) for tooth in teeth ]

        # Ratios are all relative to the inner most gear which is 1
        ratios = [ 0 ] * len(teeth)
        tp = len(teeth) - 1
        ratios[tp] = 1.0
        while tp > 0:
            tp -= 1
            ratios[tp] = ratios[tp+1] * float(teeth[tp+1]) / teeth[tp]
    
        # Number of points is based on the lowest common multiple of all of the teeth
        points = self.lcmList( teeth )
        resolution = params.resolution if points * params.resolution < self.MAX_POINTS else self.MAX_POINTS / float(points)
        points = int( points * resolution )
        mult = (2.0 * pi) / float(params.resolution * min([abs(t) for t in teeth]))

        chain = []
        for tooth in range( points + 1):
            a = 0.0
            x, y = params.xCenter, params.yCenter
            for r, rat in zip( radii, ratios ):
                a += rat * tooth * mult
                x += r * cos(a)
                y += r * sin(a)
            chain.append( (x,y) )
        chains = Chains.autoScaleCenter( [chain], [ (params.xCenter-params.radius, params.yCenter-params.radius), (params.xCenter+params.radius,params.yCenter+params.radius) ] )
        if params.fitToTable:
            chains = [ Chains.circleToTable( c, TABLE_WIDTH, TABLE_LENGTH ) for c in chains ]
        return chains

    def gcd( self, a, b ):
        """Geatest Common Divisor - Euclid"""
        while b:
            a, b = b, a % b
        return a

    def lcm( self, a, b ):
        """Lowest Common Multiple"""
        return a * b // self.gcd( a, b )

    def gcdList( self, numbers ):
        """Greatest Common Divisor for a list of numbers"""
        return reduce( self.gcd, numbers )

    def lcmList( self, numbers ):
        """Lowest Common Multiple for a list of numbers"""
        return reduce( self.lcm, numbers )

