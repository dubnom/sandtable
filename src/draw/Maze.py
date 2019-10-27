import random
from dialog import DialogInt, DialogBreak, DialogFloat
from sandable import Sandable


class Sander(Sandable):
    """
### Draw a maze. Start at the lower left corner and end at the upper right corner.

Thanks to David Bau who provided the basis of the maze generator code.

#### Hints

Pressing the *Random* button will draw a new maze.

#### Parameters

* **Columns and Rows** - number of maze lines. Higher numbers create a denser,
  harder maze while smaller numbers create a sparser, easier maze.
* **Random seed** - this is used to generate random mazes.  Different seeds generate different mazes.
  The *Random* button will create new seeds (and mazes)  automatically.
* **Width** and **Length** - how big the maze should be. Probably not worth changing.
* **Starting locations** - where on the table the maze should be drawn. Also normally not worth changing.
"""

    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3

    B_LEFT = 0x04
    B_UP = 0x02
    B_RIGHT = 0x01
    B_DOWN = 0x08
    B_SET = 0x10

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogInt("columns",     "Columns",                  default=int(width/(ballSize*1.25)), min=3, max=int(width/ballSize)),
            DialogInt("rows",        "Rows",                     default=int(length/(ballSize*1.25)), min=3, max=int(length/ballSize)),
            DialogInt("seed",        "Random seed",              default=1, min=0, max=10000.0, rbutton=True),
            DialogBreak(),
            DialogFloat("width",       "Width",                    default=width, units=units, min=1.0, max=width),
            DialogFloat("length",      "Length",                   default=length, units="units", min=1.0, max=length),
            DialogFloat("xOffset",     "Starting x location",      default=0.0, units=units),
            DialogFloat("yOffset",     "Starting y location",      default=0.0, units=units),
        ]

    def generate(self, params):
        random.seed(params.seed)

        cols = params.columns
        rows = params.rows
        maze = self.makeMaze(cols, rows)

        # turn the maze into chains
        xScale = params.width / (cols - 1)
        yScale = params.length / (rows - 1)
        dir = self.RIGHT
        x, y = 0, 0
        chain = []
        while True:
            chain.append((params.xOffset + xScale * x, params.yOffset + yScale * y))
            edges = maze[y * cols + x]
            if dir == self.RIGHT:
                if edges & self.B_UP:
                    dir = self.UP
                elif edges & self.B_RIGHT:
                    dir = self.RIGHT
                elif edges & self.B_DOWN:
                    dir = self.DOWN
                else:
                    dir = self.LEFT
            elif dir == self.UP:
                if edges & self.B_LEFT:
                    dir = self.LEFT
                elif edges & self.B_UP:
                    dir = self.UP
                elif edges & self.B_RIGHT:
                    dir = self.RIGHT
                else:
                    dir = self.DOWN
            elif dir == self.LEFT:
                if edges & self.B_DOWN:
                    dir = self.DOWN
                elif edges & self.B_LEFT:
                    dir = self.LEFT
                elif edges & self.B_UP:
                    dir = self.UP
                else:
                    dir = self.RIGHT
            else:  # dir == self.DOWN
                if edges & self.B_RIGHT:
                    dir = self.RIGHT
                elif edges & self.B_DOWN:
                    dir = self.DOWN
                elif edges & self.B_LEFT:
                    dir = self.LEFT
                else:
                    dir = self.UP

            if dir == self.UP:
                y += 1
            elif dir == self.DOWN:
                y -= 1
            elif dir == self.LEFT:
                x -= 1
            else:
                x += 1

            if x < 0 or x > cols or y < 0 or y > rows:
                break
        return [chain]

    def makeMaze(self, w, h):
        over = False
        maze = [0] * w * h
        path = random.sample([pos for pos in range(w * h) if maze[pos] == 0], 1)
        nextdir = -1
        while path:
            pos = path[-1]
            choices = [d for d in range(4) if self.canbuild(maze, w, h, pos, d, over)]
            if nextdir in choices and random.randint(0, 1) == 0:
                pass
            elif choices:
                nextdir = random.sample(choices, 1)[0]
            else:
                path.pop()
                continue
            path.append(self.dobuild(maze, w, h, pos, nextdir, over))
        # Mark the entry point
        maze[0] |= self.B_LEFT
        # Mark the exit point
        # maze[w * h - 1] |= self.B_RIGHT
        return maze

    def dobuild(self, maze, w, h, pos, d, over):
        offset = (1, w, -1, -w)[d]
        maze[pos] |= 1 << d
        pos += offset
        while maze[pos]:
            maze[pos] ^= random.choice((0, 15))
            maze[pos] |= self.B_SET
            pos += offset
        maze[pos] |= 1 << (d ^ 2)
        return pos

    def canbuild(self, maze, w, h, pos, dir, over):
        if dir < 0:
            return False
        offset = (1, w, -1, -w)[dir]
        while not self.atedge(w, h, pos, dir):
            pos += offset
            if maze[pos] == 0:
                return True
            if not over or not self.cancross(maze, pos, dir):
                return False
        return False

    def atedge(self, w, h, pos, dir):
        if dir == self.LEFT:
            return pos % w == w - 1
        if dir == self.UP:
            return pos >= w * (h - 1)
        if dir == self.RIGHT:
            return pos % w == 0
        if dir == self.DOWN:
            return pos < w

    def cancross(self, maze, pos, dir):
        return maze[pos] & 15 == (10, 5, 10, 5)[dir]
