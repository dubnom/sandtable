from math import radians, sin, cos, pow
from Sand import *
from dialog import *
from Chains import *

class Sines( Sandable ):
    """
        <h3>Draw interfering sine waves around a spiral</h3>

        <ul>
         <li><i>Lines per Inch</i> - number of lines drawn within an inch of the spiral.
             Changing this can make the lines closer together (try a number like 10) or farther apart (try 0.5).
         <li><i>Starting angle</i> - the angle the spiral starts at. The default of 0.0 starts to the right of center.
         <li><i>Sample rate</i> - how frequently points are calculated around the spiral.  Smaller numbers create rounder
             spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
             121 to get a rotating triangle; 74 makes a rotating pentagon.
         <li><i>Growth base power</i> - how quickly the outer rings of the spiral get farther from each other.
             The default of 1.0 creates a linear spiral, try 2.0 or more for a spiral that grows faster
             and 0.5 for a spiral that is big in the center.
         <li><i>Wave frequency(s)</i> - a list of wave frequencies, or more simply put - the number of waves for each
             rotation of the spiral.  If the number is an integer, the number of waves will remain in place from line-to-line.
             Non-integers will draw the whole-number of waves and leave a bit over for the decimal. If the number isn't too far from
             an integer it will look like a slowly rotating figure. If the number is further away, the figure will rotate quickly
             and create patterns that "interfere" with one another (in a pleasant way).<br>
             More than one frequency can be given. When this is combined with different <i>Wave amplitudes</i> and <i>Wave phases</i>
             complex and interesting figures emerge.
         <li><i>Wave amplitude(s)</i> - the height, in inches, of each wave.
         <li><i>Wave phase(s)</i> - the starting phase, in degrees, of each wave.
         <li><i>Inner radius</i> and <i>Outer radius</i> - how far from the center the spiral should start and end.
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the spiral will be relative to the table.
        </ul>

        <blockquote>
         <table>
          <tr><th></th><th>Parameter</th><th colspan=3>Waves</th><th>Radii</th></tr>
          <tr><th>Description</th><th>LPI, Start, Sample, Growth</th><th>Freqs</th><th>Amps</th><th>Phases</th><th>Inner, Outer</th></tr>
          <tr><td>Spiraling Boxy</td><td>5, 0, 5, 1</td><td>4.1</td><td>1</td><td>0</td><td>1, 8</td></tr>
          <tr><td>Gentler Boxy</td><td>3, 0, 5, 1</td><td>4.05</td><td>1</td><td>0</td><td>1, 8</td></tr>
          <tr><td>Wobbly Boxy</td><td>1, 0, 5, 1</td><td>4.05, 7</td><td>1, .5</td><td>0, 0</td><td>1, 8</td></tr>
          <tr><td>Spiky</td><td>1, 0, 5, 1</td><td>24</td><td>1</td><td>0</td><td>1, 8</td></tr>
          <tr><td>Messy Triangle</td><td>1.25, 0, 5, 1</td><td>3.1, 25.5</td><td>1, .5</td><td>0, 0</td><td>1, 8</td></tr>
         </table>
        </blockquote>"""

    def __init__( self, width, length ):
        radius = min(width,length) / 2.0
        mRadius = max(width,length) / 2.0
        self.editor = [
            DialogFloat( "linesPerInch",    "Lines per Inch",       default = 3.0, min = 0.001, max = 32.0 ),
            DialogFloat( "angleStart",      "Starting angle",       units = "degrees" ),
            DialogFloat( "angleRate",       "Sample rate",          units = "degrees", default = 5.0 ),
            DialogFloat( "base",            "Growth base power",    default = 1.0, min = 0.001 ),
            DialogFloats("frequencies",     "Wave frequency(s)",    units = "f1,f2,...", default=[6,30], min=1.0, max=60.0, minNums=1, maxNums=3 ),
            DialogFloats("amplitudes",      "Wave amplitude(s)",    units = "inches a1,a2,...", default=[1,.5], min=0.1, max=2.0, minNums=1, maxNums=3 ),
            DialogFloats("phases",          "Wave phase(s)",        units = "degrees p1,p2,...", default=[0,0], min=0.0, max=360.0, minNums=1, maxNums=3, rRound=0 ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
            DialogFloat( "innerRadius",     "Inner radius",         units = "inches", default = radius * 0.15, min = 0.0, max = mRadius ),
            DialogFloat( "outerRadius",     "Outer radius",         units = "inches", default = radius, min = 1.0, max = mRadius ),
        ]

    def generate( self, params ):
        frequencies = params.frequencies
        amplitudes  = params.amplitudes
        phases      = params.phases
        fap = list(zip( frequencies, amplitudes, list(map( radians, phases ))))
        
        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius

        chain = []
        if params.angleRate:
            xCenter = params.xCenter
            yCenter = params.yCenter
            
            thickness = params.outerRadius - params.innerRadius
            points = int( (360.0 / abs(params.angleRate)) * params.linesPerInch * (params.outerRadius - params.innerRadius))
            divisor = pow((points * abs(params.angleRate)) / 360.0, params.base)
            point360 = 360.0 / abs( params.angleRate )
            
            for point in range( points ):
                angle   = params.angleStart + radians( point * params.angleRate )
                radius  = params.innerRadius + thickness * (pow(((point * abs(params.angleRate)) / 360.0), params.base) / divisor)
                for f, a, p in fap:
                    radius += sin( angle * f + p ) * a 
                x = xCenter + (cos( angle ) * radius)
                y = yCenter + (sin( angle ) * radius)
                chain.append( (x,y) )
        if params.fitToTable:
            chain = Chains.circleToTable( chain, TABLE_WIDTH, TABLE_LENGTH )
        return [chain]

