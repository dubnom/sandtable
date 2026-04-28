from math import pi

import numpy as np

from Chains import Chains
from dialog import DialogBreak, DialogFloat, DialogInt, DialogList
from sandable import SandException, Sandable


class Sander(Sandable):
    # Per-style valid parameter zones: (feed_lo, feed_hi, offset_lo, offset_hi)
    # kill = feed + offset, so kill is always expressed relative to feed.
    # Each zone is constrained to the Gray-Scott pattern-forming region so any
    # combination of feedVal/killVal (1-100) produces a patterned field.
    ZONES = {
        "Custom":        (0.018, 0.058, 0.010, 0.038),
        "Spots":         (0.018, 0.038, 0.028, 0.040),
        "Labyrinth":     (0.028, 0.050, 0.022, 0.034),
        "Coral":         (0.040, 0.065, 0.004, 0.018),
        "Split-Stripes": (0.013, 0.030, 0.023, 0.034),
    }

    # feedVal/killVal encode the zone position (1-100) for each preset's
    # known-good center point.
    PRESETS = {
        "Custom": {},
        "Spots": {
            "iterations": 1100,
            "feedVal": 61,   # f=0.030
            "killVal": 41,   # offset=0.032
            "seedCount": 9,
            "seedRadius": 3,
            "levels": 5,
        },
        "Labyrinth": {
            "iterations": 900,
            "feedVal": 40,   # f=0.0367
            "killVal": 48,   # offset=0.0282
            "seedCount": 10,
            "seedRadius": 4,
            "levels": 6,
        },
        "Coral": {
            "iterations": 1400,
            "feedVal": 58,   # f=0.0545
            "killVal": 20,   # offset=0.0075
            "seedCount": 7,
            "seedRadius": 3,
            "levels": 7,
        },
        "Split-Stripes": {
            "iterations": 1200,
            "feedVal": 53,   # f=0.022
            "killVal": 51,   # offset=0.029
            "seedCount": 6,
            "seedRadius": 5,
            "levels": 6,
        },
    }

    """
### Draw reaction-diffusion contours

#### Hints

Try **Preset** first, then adjust **Feed** and **Kill** to explore variations within that style.

#### Parameters

* **Preset** - quick starting point for spots, labyrinths, coral, or split-stripe families.
* **Grid Cells** - simulation resolution. Higher values create finer detail but take longer.
* **Iterations** - number of Gray-Scott simulation steps.
* **Feed** (1-100) - controls how fast new material enters. The meaning shifts with each preset style.
* **Kill** (1-100) - relative modifier of Feed; higher values pull the pattern toward a different family boundary.
* **Diffusion A** and **Diffusion B** - diffusion speeds of the two simulated chemicals.
* **Seed Count** and **Seed Radius** - number and size of the initial disturbances.
* **Contour Levels** - number of contour bands extracted from the final field.
* **Simplify spacing** - minimum spacing between kept points in output chains.
* **X and Y Origin** - lower-left corner of the active region.
* **Width** and **Length** - size of the active region.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogList("preset", "Preset", default="Labyrinth", list=list(self.PRESETS.keys())),
            DialogInt("cells", "Grid Cells", default=60, min=30, max=90),
            DialogInt("iterations", "Iterations", default=60, min=30, max=200),
            DialogInt("feedVal", "Feed", default=50, min=1, max=100),
            DialogInt("killVal", "Kill (relative to feed)", default=50, min=1, max=100),
            DialogFloat("diffA", "Diffusion A", default=1.0, min=0.1, max=2.0),
            DialogFloat("diffB", "Diffusion B", default=0.5, min=0.05, max=1.5),
            DialogInt("seedCount", "Seed Count", default=20, min=10, max=50),
            DialogInt("seedRadius", "Seed Radius", default=4, min=1, max=12),
            DialogInt("levels", "Contour Levels", default=6, min=1, max=16),
            DialogFloat("simplify", "Simplify spacing", units=units, default=0.25, min=0.0, max=1.0),
            DialogInt("randomSeed", "Random Seed", default=1, min=0, max=999999),
            DialogBreak(),
            DialogFloat("xOffset", "X Origin", units=units, default=0.0),
            DialogFloat("yOffset", "Y Origin", units=units, default=0.0),
            DialogFloat("width", "Width", units=units, default=width, min=1.0, max=1000.0),
            DialogFloat("length", "Length", units=units, default=length, min=1.0, max=1000.0),
        ]
        self.ballSize = ballSize

    def _apply_preset(self, params):
        preset = self.PRESETS.get(getattr(params, "preset", "Custom"), {})
        for name, value in preset.items():
            setattr(params, name, value)
        return params

    def _map_params(self, params):
        """Convert feedVal/killVal (1-100) to real Gray-Scott feed/kill values.
        kill = feed + offset so killVal is genuinely relative to the feed level.
        """
        style = getattr(params, "preset", "Custom")
        f_lo, f_hi, off_lo, off_hi = self.ZONES.get(style, self.ZONES["Custom"])
        t_feed = (int(params.feedVal) - 1) / 99.0
        t_kill = (int(params.killVal) - 1) / 99.0
        params.feed = f_lo + t_feed * (f_hi - f_lo)
        params.kill = params.feed + off_lo + t_kill * (off_hi - off_lo)
        return params

    def _seed_field(self, cells, seed_count, seed_radius, random_seed):
        a = np.ones((cells, cells), dtype=np.float64)
        b = np.zeros((cells, cells), dtype=np.float64)
        rng = np.random.default_rng(int(random_seed))

        # Always seed the center so low seed counts still generate structure.
        spots = [(cells // 2, cells // 2)]
        for _ in range(max(0, seed_count - 1)):
            spots.append((
                int(rng.integers(seed_radius, cells - seed_radius)),
                int(rng.integers(seed_radius, cells - seed_radius)),
            ))

        yy, xx = np.ogrid[:cells, :cells]
        for cx, cy in spots:
            mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= seed_radius ** 2
            b[mask] = 1.0
            a[mask] = 0.0
        return a, b

    def _laplacian(self, arr):
        return (
            -arr
            + 0.2 * (np.roll(arr, 1, 0) + np.roll(arr, -1, 0) + np.roll(arr, 1, 1) + np.roll(arr, -1, 1))
            + 0.05 * (
                np.roll(np.roll(arr, 1, 0), 1, 1)
                + np.roll(np.roll(arr, 1, 0), -1, 1)
                + np.roll(np.roll(arr, -1, 0), 1, 1)
                + np.roll(np.roll(arr, -1, 0), -1, 1)
            )
        )

    def _simulate(self, params):
        a, b = self._seed_field(params.cells, params.seedCount, params.seedRadius, params.randomSeed)
        for _ in range(params.iterations):
            reaction = a * b * b
            a += self._laplacian(a) * params.diffA - reaction + params.feed * (1.0 - a)
            b += self._laplacian(b) * params.diffB + reaction - (params.kill + params.feed) * b
            np.clip(a, 0.0, 1.0, out=a)
            np.clip(b, 0.0, 1.0, out=b)
        return b

    def _interp(self, p1, p2, v1, v2, level):
        if abs(v2 - v1) < 1e-12:
            return ((p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5)
        t = (level - v1) / (v2 - v1)
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))

    def _segments_for_level(self, field, level):
        table = {
            0: [],
            1: [(3, 0)],
            2: [(0, 1)],
            3: [(3, 1)],
            4: [(1, 2)],
            5: [(3, 2), (0, 1)],
            6: [(0, 2)],
            7: [(3, 2)],
            8: [(2, 3)],
            9: [(0, 2)],
            10: [(0, 1), (2, 3)],
            11: [(1, 2)],
            12: [(1, 3)],
            13: [(0, 1)],
            14: [(3, 0)],
            15: [],
        }
        cells = field.shape[0]
        segments = []
        for y in range(cells - 1):
            for x in range(cells - 1):
                bl = field[y, x]
                br = field[y, x + 1]
                tr = field[y + 1, x + 1]
                tl = field[y + 1, x]
                idx = 0
                if bl >= level:
                    idx |= 1
                if br >= level:
                    idx |= 2
                if tr >= level:
                    idx |= 4
                if tl >= level:
                    idx |= 8
                if idx == 0 or idx == 15:
                    continue

                points = {
                    0: self._interp((x, y), (x + 1, y), bl, br, level),
                    1: self._interp((x + 1, y), (x + 1, y + 1), br, tr, level),
                    2: self._interp((x, y + 1), (x + 1, y + 1), tl, tr, level),
                    3: self._interp((x, y), (x, y + 1), bl, tl, level),
                }
                for e1, e2 in table[idx]:
                    segments.append((points[e1], points[e2]))
        return segments

    def _join_segments(self, segments):
        def key(point):
            return (round(point[0], 5), round(point[1], 5))

        chains = []
        unused = [(a, b) for a, b in segments]
        while unused:
            a, b = unused.pop()
            chain = [a, b]
            changed = True
            while changed:
                changed = False
                start_key = key(chain[0])
                end_key = key(chain[-1])
                for i, (p1, p2) in enumerate(unused):
                    k1 = key(p1)
                    k2 = key(p2)
                    if k1 == end_key:
                        chain.append(p2)
                    elif k2 == end_key:
                        chain.append(p1)
                    elif k2 == start_key:
                        chain.insert(0, p1)
                    elif k1 == start_key:
                        chain.insert(0, p2)
                    else:
                        continue
                    del unused[i]
                    changed = True
                    break
            if len(chain) > 1:
                chains.append(chain)
        return chains

    def _scale_chains(self, chains, params):
        scale_x = params.width / (params.cells - 1)
        scale_y = params.length / (params.cells - 1)
        return [[
            (x * scale_x, y * scale_y)
            for x, y in chain
        ] for chain in chains]

    def _fallback_params(self, params):
        """Return params overridden with Labyrinth defaults (a known-good state)."""
        from copy import copy
        fb = copy(params)
        fb.preset = "Labyrinth"
        for k, v in self.PRESETS["Labyrinth"].items():
            setattr(fb, k, v)
        return self._map_params(fb)

    def generate(self, params):
        params = self._apply_preset(params)
        params = self._map_params(params)
        if params.cells < 3:
            raise SandException("Grid Cells must be at least 3")

        field = self._simulate(params)
        fmin = float(field.min())
        fmax = float(field.max())
        if abs(fmax - fmin) < 1e-9:
            # The chosen feed/kill combination produced no pattern; silently
            # retry with the Labyrinth defaults so a result is always returned.
            field = self._simulate(self._fallback_params(params))
            fmin = float(field.min())
            fmax = float(field.max())
            if abs(fmax - fmin) < 1e-9:
                raise SandException("Reaction-diffusion field is flat; try different feed/kill values")

        span = fmax - fmin
        low = fmin + span * 0.35
        high = fmin + span * 0.85
        levels = np.linspace(low, high, int(params.levels))

        chains = []
        for level in levels:
            segments = self._segments_for_level(field, float(level))
            chains.extend(self._join_segments(segments))

        chains = self._scale_chains(chains, params)
        if params.simplify > 0.0:
            chains = Chains.deDistances(chains, epsilon=params.simplify)
        chains = [chain for chain in Chains.deDupe(chains, epsilon=max(params.simplify * 0.5, 0.001)) if len(chain) > 1]
        if not chains:
            raise SandException("No contours were generated; try more iterations or different feed/kill values")
        # Convert separate islands into scanline-connected motion to avoid long
        # hidden jumps between disjoint contour areas.
        return Chains.scanalize(chains, params.xOffset, params.yOffset, params.width, params.length, 1.0 / self.ballSize)