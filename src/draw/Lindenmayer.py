from sandable import Sandable
from dialog import DialogInt, DialogFloat, DialogBreak, DialogStr, DialogYesNo
from PolyLine import PolyLine
from Chains import Chains


class Sander(Sandable):
    """
### Simple movement/substitution language for creating complex fractals

#### Hints

Read the Wikipedia article on [L-systems](http://en.wikipedia.org/wiki/L-system). All of their examples should work.

#### Parameters

* **Repetitions** - number of times to run through replacing **Axiom** with **Rules**.
* **Angle** - number of degrees to turn.
* **Axiom** - Starting string to iteratively apply **Rules** to.
* **Rules** - Replacement rules of the form X=Y where all occurences of "X" will be replaced by "Y".
* **X and Y Origin** - lower lefthand corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the drawing should be. Probably not worth changing.

#### Quick primer on L-systems

Special characters used in **Axiom** and **Rules**:

* **A, B, F** - Move forward and draw a line.
* **+** - Turn left by **Angle** degrees.
* **-** - Turn right by **Angle** degrees.
* **|** - Turn around (180 degrees).
* **[** - Push the current location onto a stack.
* **]** - Draw an efficient, non-destructive path, back to a previously pushed location.

A simple **Axiom** that would draw a square is "F-F-F-F" with **Angle**=90 degrees.

Another simple **Axiom** that draws a triangle is "A-A-A" with **Angle**=120 degrees.

Set **Axiom**="A" and **Rule 1**="A=A+A-F-A+A", **Repetitions**=1, **Angle**=90 degrees.
The first iteration will replace every 'A' in the **Axiom** (there is only one) with "A+A-F-A+A".
We only specified one **Repetition**, so this would yield:

Forward, Turn left, Forward, Turn Right, Forward, Turn Right, Forward, Turn Left
or something that looks like:

        +--+
        |  |
      --+  +--

If you set **Repetitions**=2 then each 'A' will again be replaced by "A+A-F-A+A" and **Axiom** will
become: "A+A-F-A+A+A+A-F-A+A-F-A+A-F-A+A+A+A-F-A+A".

Visually, this will start looking like a filled-in
stepped pyramid.  Try higher values for **Repetitions** but realize that the drawing gets exponentially larger
for ever increment. The final length of **Axiom**, and the number of points in the drawing, are limited
to keep from running out of memory.

#### Examples

Name | Axiom | Angle | Rules
--- | --- | --- | ---
Koch Curve | F | 90 | F=F+F-F-F+F
Koch Island | F+F+F+F | -90 | F=F+F-F-FF+F+F-F
Koch Snowflake | F++F++F | 60 | F=F-F++F-F
Sierpinski Triangle | F-G-G | 120 | F=F-G+F+G-F, G=GG
Dragon Curve | FX | 90 | X=X+YF+, Y=-FX-Y
Fractal Plant | X | 25 | X=F+[[X]-X]-F[-FX]+X, F=FF
Rings | F-F-F-F | 90 | F=FF-F-F-F-F-F+F
Hilbert Curve | X | -90 | X=-YF+XFX+FY-, Y=+XF-YFY-FX+
Pentaplexity | F++F++F++F++F | 36 | F=F++F++F|F-F++F
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogInt("repetitions",        "Repetitions",          default=3, min=1, max=20),
            DialogFloat("heading",          "Initial heading",      units="degrees", default=0.0),
            DialogFloat("angle",            "Angle",                units="degrees", default=90.0),
            DialogYesNo("round",            "Rounded edges",        default=False),
            DialogBreak(),
            DialogStr("axiom",              "Axiom",                length=30),
            DialogStr("rule1",              "Rule 1",               length=30),
            DialogStr("rule2",              "Rule 2",               length=30),
            DialogStr("rule3",              "Rule 3",               length=30),
            DialogStr("rule4",              "Rule 4",               length=30),
            DialogStr("rule5",              "Rule 5",               length=30),
            DialogStr("rule6",              "Rule 6",               length=30),
            DialogBreak(),
            DialogFloat("xOrigin",          "X Origin",             units=units, default=0.0),
            DialogFloat("yOrigin",          "Y Origin",             units=units, default=0.0),
            DialogFloat("width",            "Width",                units=units, default=width),
            DialogFloat("length",           "Length",               units=units, default=length),
        ]
        self.MAX_LEN = 50000

    def generate(self, params):
        # Compile the rules
        rules = {}
        for key in params.keys():
            if key.startswith('rule'):
                values = getattr(params, key).split('=')
                if len(values) == 2:
                    rules[values[0]] = values[1]

        # Convert the axiom into fully expanded string
        path = self._iterateAxiom(params.axiom, rules, params.repetitions)

        # Convert the axiom into a polyline
        polyline = PolyLine()
        polyline.turn(params.heading)
        methods = {'F': lambda: polyline.forward(1.0),
                   'A': lambda: polyline.forward(1.0),
                   'B': lambda: polyline.forward(1.0),
                   '-': lambda: polyline.turn(-params.angle),
                   '+': lambda: polyline.turn(params.angle),
                   '|': lambda: polyline.turn(180.0),
                   '[': lambda: polyline.push(),
                   ']': lambda: polyline.pop(),
                   }

        for char in path:
            if char in methods:
                methods[char]()

        chains = [polyline.points]
        if params.round:
            chains = Chains.splines(chains)
        bounds = [(params.xOrigin, params.yOrigin), (params.width, params.length)]
        return Chains.autoScaleCenter(chains, bounds)

    def _iterateAxiom(self, axiom=None, rules=None, repetitions=1):
        for repeat in range(0, repetitions):
            newpath = ""
            i = 0
            length = len(axiom)
            while i < length and length - i + len(newpath) < self.MAX_LEN:
                for old, new in rules.items():
                    if old == axiom[i:i + len(old)]:
                        newpath += new
                        i += len(old)
                        break
                else:
                    newpath += axiom[i]
                    i += 1
            axiom = newpath
            if i < length:
                break
        return axiom
