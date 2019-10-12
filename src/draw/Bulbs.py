from math import pow, radians, sin, cos
from Sand import *
from dialog import *

class Bulbs( Sandable ):
    """
        <h3>Bulbs can create interesting flower-like images and beautiful geometric patterns</h3>

        The formula works by imposing a sine wave of <i>Major frequency</i> and <i>Major amplitude</i> on top of a simple spiral.
        <i>Minor frequency</i> and <i>Minor amplitude</i> are used to modify the sine wave by moving it forward or back a bit
        as it goes around - small numbers create ripples, large numbers create cool interference patterns.

        <ul>
         <li><i>Major frequency</i> - how many bumps to put on the spiral.
         <li><i>Major amplitude</i> - size of the bumps in inches.
         <li><i>Minor frequency</i> - how often to bend the major bumps forward and backward (numbers close to Major frequency are a good place to start).
         <li><i>Minor amplitude</i> - size of the bending in degrees. Smaller numbers are more subtle, larger numbers create greater folds.
         <li><i>Inner radius</i> and <i>Outer radius</i> - how far from the center the spiral should start and end.
         <li><i>Lines per Inch</i> - number of lines drawn within an inch of the spiral.
             Changing this can make the lines closer together (try a number like 10) or farther apart (try 0.5).
         <li><i>Sample rate</i> - angular spacing between points calculated around a 360 degree spiral.
             Smaller numbers create rounder drawings while larger numbers create spiked shapes.
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the spiral will be relative to the table."""

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "majorFreq",       "Major frequency",      units = "per rotation", default=3.0, min=0.0, max=179.0, randRange=(0.1,20.)),
            DialogFloat( "majorAmp",        "Major amplitude",      units = "inches", default=4.0, min=0.0, max=max(width,length) / 2.0),
            DialogFloat( "minorFreq",       "Minor frequency",      units = "per rotation", default=3.02, min=0.0, max=179.0, randRange=(0.1,20.)),
            DialogFloat( "minorAmp",        "Minor amplitude",      units = "degrees", default=20.0, min=0.0, max=90.0 ),
            DialogBreak(),
            DialogFloat( "innerRadius",     "Inner radius",         units = "inches", default=1.0, min=0.0, max=max(width,length) ),
            DialogFloat( "outerRadius",     "Outer radius",         units = "inches", default=min(width,length)/2, min=1.0, max=max(width,length)*1.5 ),
            DialogFloat( "linesPerInch",    "Lines per Inch",       default = 3.0, min = 0.1, max = 10.0 ),
            DialogInt(   "angleRate",       "Sample rate",          units = "degrees", default = 5, min = 1, max = 10 ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
       ] 

    def generate( self, params ):
        chain = []
        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius
        if params.angleRate:
            xCenter, yCenter = params.xCenter, params.yCenter
            points = int( (360.0 / abs(params.angleRate)) * params.linesPerInch * (params.outerRadius - params.innerRadius))
            thickness = (params.outerRadius - params.innerRadius) / points
            
            majorFreq = params.majorFreq
            minorFreq = params.minorFreq

            for point in range( points ):
                angle   = point * params.angleRate
                radius  = params.innerRadius + thickness * point
                radius += params.majorAmp * sin( radians( angle * majorFreq ))
                angle1  = radians(angle + params.minorAmp * sin( radians( angle * minorFreq )))
                x = xCenter + radius * cos(angle1)
                y = yCenter + radius * sin(angle1)
                chain.append( (x,y) )

        return [chain]

