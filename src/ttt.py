"""
Thanks to Chris Radek <chris@timeguy.com> for creating TrueTypeTracer
which was the inspiration for this python native code.
"""
from fontTools import ttLib
from fontTools.pens.basePen import BasePen

MYFSIZE = 64
TTFONT = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"


class PolylinesPen(BasePen):
    """Convert font drawing pen movements into an array of polylines."""

    def __init__(self, glyphSet):
        BasePen.__init__(self, glyphSet)
        self._polyline = []
        self.polylines = []

    def _moveTo(self, pt):
        if len(self._polyline):
            self.polylines.append(self._polyline)
        self._polyline = [pt]

    def _lineTo(self, pt):
        self._polyline.append(pt)

    def _curveToOne(self, pt1, pt2, pt3):
        # draw a cubic spline from pt0 to 'pt3' using pt1,pt2
        # Cubic Bezier curves (a compound curve)
        # B(t)=A(1-t)^3 + 3Bt(1-t)^2 + 3Ct^2(1-t) + Dt^3 , t in [0,1].
        def SQ(a): return a*a
        def CUBE(a): return a*a*a
        CSTEPS = 10

        xp, yp = self._polyline[-1]
        for t in range(CSTEPS):
            tf = float(t+1)/CSTEPS
            x = CUBE(1.-tf)*xp + SQ(1-tf)*3.*tf*pt1[0] + SQ(tf)*(1.-tf)*3.*pt2[0] + CUBE(tf)*pt3[0]
            y = CUBE(1.-tf)*yp + SQ(1-tf)*3.*tf*pt1[1] + SQ(tf)*(1.-tf)*3.*pt2[1] + CUBE(tf)*pt3[1]
            self._polyline.append((x, y))

    def _closePath(self):
        if len(self._polyline) > 0:
            self.polylines.append(self._polyline)


class TrueTypeTracer():
    """Chris Radek's algorithm for converting fonts into polylines."""

    def __init__(self, ttfont=TTFONT, text='', height=1.):
        def iswgcodesafe(c): return 32 < ord(c) < 128
        def isgcodesafe(c): return 32 < ord(c) < 128

        self._ttfont = ttfont
        self._face = ttLib.TTFont(ttfont)
        self._unitsPerEm = float(self._face['head'].unitsPerEm)
        self._scale = height / self._unitsPerEm

    def _render_char(self, glyphs, glyph):
        """Convert glyphs into outlines (as polylines)."""
        pPen = PolylinesPen(glyphs)
        glyph.draw(pPen, 0)
        if not len(pPen.polylines):
            return None
        return pPen.polylines

    def polylines(self, text=''):
        xoffset = 0
        lastC = None
        pls = []

        # loop through rendering all the chars in the string
        cmap = self._face['cmap'].getBestCmap()
        glyphs = self._face['glyf']
        try:
            kerns = self._face['kern'].kernTables[0]
        except (IndexError, KeyError):
            kerns = None

        for c in text:
            try:
                glyph = glyphs[cmap[ord(c)]]
            except (IndexError, KeyError):
                continue

            # Kerning
            if lastC:
                try:
                    xoffset += kerns[(cmap[ord(lastC)], cmap[ord(c)])]
                except (IndexError, KeyError, TypeError):
                    pass
            lastC = c

            # Offset the character
            charPolylines = self._render_char(glyphs, glyph)
            if charPolylines:
                pls += [[(p[0]+xoffset, p[1]) for p in pl] for pl in charPolylines]
            try:
                xoffset += glyph.xMax
            except AttributeError:
                xoffset += self._unitsPerEm / 2

        return [[(x*self._scale, y*self._scale) for x, y in pl] for pl in pls]
