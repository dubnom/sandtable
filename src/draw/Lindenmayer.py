from Sand import *
from dialog import *
from PolyLine import *
from Chains import *

class Lindenmayer( Sandable ):
    """
        <h3>Simple movement/substitution language for creating complex fractals</h3>

        Hint: Read the Wikipedia article on <a href="http://en.wikipedia.org/wiki/L-system">L-systems</a>.
        The examples should work.

        <ul>
         <li><i>Repetitions</i> - number of times to run through replacing <i>Axiom</i> with <i>Rules</i>.
         <li><i>Angle</i> - number of degrees to turn.
         <li><i>Axiom</i> - Starting string to iteratively apply <i>Rules</i> to.
         <li><i>Rules</i> - Replacement rules of the form A=B where all occurences of "A" will be replaced by "B"
             in <i>Axiom</i> and subsequent iterations of <i>Axiom</i>.<br>
             "A" can be one or more letters.
             "B" can be any letters including what was specified in "A". There are special characters that are
             explained below.
         <li><i>X and Y Origin</i> - lower lefthand corner of the drawing. Usually not worth changing.
         <li><i>Width</i> and <i>Length</i> - how big the drawing should be. Probably not worth changing.
        </ul>

        Special characters used in <i>Axiom</i> and <i>Rules</i>:
        <ul>
         <li><b>A, B, F</b> - Move forward and draw a line.
         <li><b>+</b> - Turn left by <i>Angle</i> degrees.
         <li><b>-</b> - Turn right by <i>Angle</i> degrees.
         <li><b>|</b> - Turn around (180 degrees).
         <li><b>[</b> - Push the current location onto a stack.
         <li><b>]</b> - Draw an efficient, non-destructive path, back to a previously pushed location.
        </ul>

        A simple <i>Axiom</i> that would draw a square is "F-F-F-F" with <i>Angle</i>=90 degrees.<br>
        Another simple <i>Axiom</i> that draws a triangle is "A-A-A" with <i>Angle</i>=120 degrees.<br>
        <br>
        Set <i>Axiom</i>="A" and <i>Rule 1</i>="A=A+A-F-A+A", <i>Repetitions</i>=1, <i>Angle</i>=90 degrees.
        The first iteration will replace every 'A' in the <i>Axiom</i> (there is only one) with "A+A-F-A+A".
        We only specified one <i>Repetition</i>, so this would yield:<br>
        <pre>
        Forward, Turn left, Forward, Turn Right, Forward, Turn Right, Forward, Turn Left
        or something that looks like:         +--+
                                              |  |
                                            --+  +--
        </pre>
        If you set <i>Repetitions</i>=2 then each 'A' will again be replaced by "A+A-F-A+A" and <i>Axiom</i> will
        become: "A+A-F-A+A+A+A-F-A+A-F-A+A-F-A+A+A+A-F-A+A".<br>
        Visually, this will start looking like a filled-in
        stepped pyramid.  Try higher values for <i>Repetitions</i> but realize that the drawing gets exponentially larger
        for ever increment. The final length of <i>Axiom</i>, and the number of points in the drawing, are limited
        to keep from running out of memory.
        """

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "repetitions",     "Repetitions",          default = 3, min = 1, max = 20 ),
            DialogFloat( "angle",           "Angle",                units = "degrees", default = 90.0 ),
            DialogBreak(),
            DialogStr(   "axiom",           "Axiom",                length = 30 ),
            DialogStr(   "rule1",           "Rule 1",               length = 30 ),
            DialogStr(   "rule2",           "Rule 2",               length = 30 ),
            DialogStr(   "rule3",           "Rule 3",               length = 30 ),
            DialogStr(   "rule4",           "Rule 4",               length = 30 ),
            DialogStr(   "rule5",           "Rule 5",               length = 30 ),
            DialogStr(   "rule6",           "Rule 6",               length = 30 ),
            DialogBreak(),
            DialogFloat( "xOrigin",         "X Origin",             units = "inches", default = 0.0 ),
            DialogFloat( "yOrigin",         "Y Origin",             units = "inches", default = 0.0 ),
            DialogFloat( "width",           "Width",                units = "inches", default = width ),
            DialogFloat( "length",          "Length",               units = "inches", default = length ),
        ]
        self.MAX_LEN = 5000

    def generate( self, params ):
        # Compile the rules
        rules = {}
        for key in dir( params ):
            if key.startswith( 'rule' ):
                values = getattr( params, key ).split( '=' )
                if len( values ) == 2:
                    rules[ values[0] ] = values[1]

        # Convert the axiom into fully expanded string
        path = self._iterateAxiom( params.axiom, rules, params.repetitions )

        # Convert the axiom into a polyline
        polyline = PolyLine()
        methods = { 'F': lambda:polyline.forward( 1.0 ),
                    'A': lambda:polyline.forward( 1.0 ),
                    'B': lambda:polyline.forward( 1.0 ),
                    '-': lambda:polyline.turn( -params.angle ),
                    '+': lambda:polyline.turn( params.angle ),
                    '|': lambda:polyline.turn( 180.0 ),
                    '[': lambda:polyline.push(),
                    ']': lambda:polyline.pop(),
                }
        
        for char in path:
            if char in methods:
                methods[char]()

        return Chains.autoScaleCenter( [polyline.points], [(params.xOrigin,params.yOrigin),(params.width,params.length)] ) 

    def _iterateAxiom( self, axiom=None, rules=None, repetitions=1 ):
        for repeat in range( 0, repetitions ):
            newpath = ""
            i = 0
            length = len(axiom)
            while i < length and length - i + len(newpath) < self.MAX_LEN:
                for old, new in rules.items():
                    if old == axiom[ i:i + len( old ) ]:
                        newpath += new
                        i += len( old )
                        break          
                else:
                    newpath += axiom[ i ]
                    i += 1
            axiom = newpath
            if i < length:
                break
        return axiom
