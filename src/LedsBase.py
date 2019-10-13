import colorsys
import random

class LedsBase(object):
    """Base class for LED lighting systems"""
    def __init__( self, rows, cols ):
        self.rows   = rows
        self.cols   = cols
        self.count  = 2*(rows+cols)
        self.clear()
        self.connect()

        # Rectangular led ranges
        # Top, Right, Bottom, Left
        self.rectangle = [
                list(range(0,cols)),
                list(range(cols,cols+rows)),
                list(range(cols+rows,cols*2+rows)),
                list(range(cols*2+rows,cols*2+rows*2))
        ]

    def close( self ):
        self.disconnect()

    def clear( self ):
        self.leds = [(0,0,0)] * self.count
    
    def set( self, start, rgb, end=None ):
        if end is None:
            end = start
        for led in range(start,end+1):
            self.leds[ led ] = rgb
    
    def get( self, led ):
        return self.leds[ led ]
    
    def add( self, start, rgb, end=None ):
        if end is None:
            end = start 
        for led in range(start,end+1):
            self.leds[ led ] = tuple( min( self.leds[ led ][ color ] + rgb[ color ], 255) for color in range(3))
    
    @staticmethod
    def HSB( hue, saturation, brightness ):
        red,green,blue = colorsys.hls_to_rgb( hue/360.0, brightness/100.0, saturation/100.0 )
        return (int(red*255.0), int(green*255.0), int(blue*255.0))
    
    @staticmethod
    def RGBtoHSB( rgb ):
        h,b,s = colorsys.rgb_to_hls( rgb[0]/255., rgb[1]/255., rgb[2]/255.)
        return (h*360., b*100., s*100.)

    @staticmethod
    def RGBRandom():
        return (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    
    @staticmethod
    def RGBRandomBetter():
        return LedsBase.HSB(random.random()*360., random.random()*40.+60., random.random()*30.+20.)

    @staticmethod
    def RGBPercent( rgb, percent ):
        return tuple([ c * percent for c in rgb ])

    @staticmethod
    def RGBAdd( rgb1, rgb2 ):
        return tuple([ min( c1 + c2, 255 ) for c1, c2 in zip( rgb1, rgb2 ) ])

    @staticmethod
    def RGBBlend( rgb1, rgb2, ratio ):
        r2 = 1.0 - ratio
        return [ min( c1 * ratio + c2 * r2, 255 ) for c1, c2 in zip( rgb1, rgb2 ) ]

    @staticmethod
    def RGBScintilate( rgb, roughness ):
        r1 = -roughness / 2.0
        h,s,v = colorsys.rgb_to_hsv( *( c / 255. for c in rgb))
        r,g,b = colorsys.hsv_to_rgb( h, s, min(1.0,max( 0.0, v + r1 + random.random()*roughness)))
        return (int(r*255.),int(g*255.),int(b*255.))

    @staticmethod
    def RGBDim( rgb, percent ):
        h,s,v = colorsys.rgb_to_hsv( *( c / 255. for c in rgb))
        r,g,b = colorsys.hsv_to_rgb( h, s, min(1.0,max( 0.0, v * percent)))
        return (int(r*255.),int(g*255.),int(b*255.))

    ################ Implemented by specific drivers ################

    def connect( self, params ):
        pass

    def disconnect( self ):
        pass

    def refresh( self ):
        pass
