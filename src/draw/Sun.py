from math import radians, sin, cos
from Sand import *
from dialog import *
from Chains import *
    
class Sun( Sandable ):
    """
        <h3>Draw a figure that roughly resembles the sun and its rays</h3>

        Hint: Set <i>Ray width</i>=0 for a cool effect.

        <ul>
         <li><i>Ray count</i> - number of rays.
         <li><i>Ray width</i> - width in degrees of each ray.
         <li><i>Ripples</i> - number of waves in a ray.
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the sun will be relative to the table.
         <li><i>Inner radius</i> and <i>Outer radius</i> - how far from the center the rays should start and end.
        </ul>"""

    def __init__( self, width, length ):
        radius = max(width,length) / 2.0
        self.editor = [
            DialogInt(   "rays",            "Ray count",            default = 12, min = 1, max = 60 ),
            DialogInt(   "rayWidth",        "Ray width",            units = "degrees", default = 10, min = 1, max = 60 ),
            DialogFloat( "ripples",         "Number of ripples" ,   default = 2.0, min = 0.0, max = 20.0 ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
            DialogFloat( "innerRadius",     "Inner radius",         units = "inches", default = 2.0, min = 0.0, max = radius ),
            DialogFloat( "outerRadius",     "Outer radius",         units = "inches", default = min(width,length)/2, min = 1.0, max = radius),
        ]

    def generate( self, params ):
        self.xCenter	= params.xCenter
        self.yCenter	= params.yCenter
        
        self.rayMax 	= 360
        self.rayStep	= 20
        self.rayScale	= params.outerRadius - params.innerRadius
        self.innerRadius= params.innerRadius
        
        self.rippleSize	= 0.5
        self.ripples   	= params.ripples
         
        raySpacing = 360.0 / params.rays

        chain = []
        for ray in range( params.rays ):
            angle = ray * raySpacing
            chain.extend( self.ray( angle, 1 ))
            chain.extend( self.ray( angle + params.rayWidth, -1 ))
        chain.append( chain[0] )
        if params.fitToTable:
            chain = Chains.circleToTable( chain, TABLE_WIDTH, TABLE_LENGTH )
        return [chain]
        
    def ray( self, angle, dir ):
        chain = []
        for r in range( 0, self.rayMax, self.rayStep ):
            x = self.innerRadius + self.rayScale * r / self.rayMax
            y = self.rippleSize * sin( radians( r * self.ripples )) 
            ar = radians( angle )   
            xPoint = self.xCenter + (x * cos( ar )) - (y * sin( ar ))
            yPoint = self.yCenter + (x * sin( ar )) + (y * cos( ar ))
            chain.append( (xPoint,yPoint) )
        if dir < 0:
            chain.reverse()
        return chain



