from sandable import Sandable, inchesToUnits
from dialog import DialogMulti, DialogFont, DialogFloat, DialogInt, DialogList
from Chains import Chains
from ttt import TrueTypeTracer


class Sander(Sandable):
    """
### Write text in sand

#### Hints

There are hundreds of different fonts, try some.

#### Parameters

* **Text** - one or more lines to draw.
* **Height** - height of the characters.
* **Font** - font used to draw the text.
* **Line Spacing** - the relative distance of multiple lines of **Text**.
* **Rotation Angle** - angle to rotate the text.
* **Origin** - where the text should be drawn relative to **X and Y Origin**.
* **X and Y Origin** - either the center or bottom left corner of the text.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogMulti("text",            "Text",                 default="Text"),
            DialogFont("font",            "Font",                default='/usr/share/fonts/truetype/msttcorefonts/Arial.ttf'),
            DialogFloat("cHeight",         "Height",               units=units, default=inchesToUnits(
                4.0, units), min=inchesToUnits(1.0, units), max=length, step=inchesToUnits(.5, units)),
            DialogFloat("lineSpacing",     "Line Spacing",         default=1.0, min=1.0, max=2.0, step=.25),
            DialogInt("rotate",          "Rotation Angle",       units="degrees", default=0., min=-180, max=180),
            DialogList("origin",          "Origin",               list=['BottomLeft', 'Center'], default='Center'),
            DialogFloat("xOffset",         "X Origin",             units=units, default=width / 2.0),
            DialogFloat("yOffset",         "Y Origin",             units=units, default=length / 2.0),
        ]

    def generate(self, params):
        results = []
        lines = params.text.split('\n')
        lineOffset = params.yOffset
        chains = None
        for lineNumber, line in enumerate(lines):
            if chains and len(chains) and len(chains[-1]) and lineNumber > 0 and lineNumber < len(lines):
                chains[-1].append((chains[-1][-1][0], lineOffset))
            chains = self._getTextChains(line.strip(), params.font, height=params.cHeight)
            if params.origin == 'Center':
                extents = Chains.calcExtents(chains)
                xOffset = (extents[0][0] - extents[1][0]) / 2.0
            else:
                xOffset = 0
            chains = Chains.transform(chains, (xOffset, lineOffset))
            results += chains
            lineOffset -= params.cHeight * params.lineSpacing

        extents = Chains.calcExtents(results)
        if params.rotate != 0.:
            results = Chains.transform(results, (extents[0][0]-extents[1][0], extents[0][1]-extents[1][1]))
            results = Chains.rotate(results, params.rotate)
            extents = Chains.calcExtents(results)
        if params.origin == 'Center':
            results = Chains.transform(results,
                                       (params.xOffset-extents[0][0]+(extents[0][0]-extents[1][0])/2.,
                                        params.yOffset-extents[0][1]+(extents[0][1]-extents[1][1])/2.))
        else:
            results = Chains.transform(results, (params.xOffset-extents[0][0], params.yOffset-extents[0][1]))

        return results

    def _getTextChains(self, text, font, xOffset=0.0, yOffset=0.0, height=1.0):
        ttt = TrueTypeTracer(ttfont=font, height=height)
        chains = ttt.polylines(text)

        # Reprocess the chain based on the right-most point
        chains = [self._reprocessChain(chain) for chain in chains]

        # Sort all of the chains by rightmost point
        chains.sort(key=lambda chain: chain[-1][0])
        return chains

    def _parseLine(self, line):
        m = self.reg.match(line)
        return float(m.group(1)), float(m.group(2))

    def _reprocessChain(self, chain):
        # Find the right-most point (biggest x)
        xHigh = None
        index = None
        for i, (x, y) in enumerate(chain):
            if xHigh is None or x > xHigh:
                index = i
                xHigh = x
        # Return the end of chain + start of chain
        return chain[index:] + chain[:index+1]
