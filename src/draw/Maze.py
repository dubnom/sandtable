import random
import user
from Sand import *
from dialog import *

class Maze( Sandable ):
    """
        <h3>Draw a maze. Start at the lower left corner and end at the upper right corner.</h3>

        Hint: Pressing the <i>Random</i> button will draw a new maze.

        <ul>
         <li><i>Columns and Rows per inch</i> - number of maze lines per inch. Higher numbers (try 2) create a denser,
             harder maze while smaller numbers (try .5) create a sparser, easier maze.
         <li><i>Random seed</i> - this is used to generate random mazes.  Different seeds generate different mazes.
             The <i>Random</i> button will create new seeds (and mazes)  automatically.
         <li><i>Width</i> and <i>Length</i> - how big the maze should be. Probably not worth changing.
         <li><i>Starting locations</i> - where on the table the maze should be drawn. Also normally not worth changing.
        </ul>

        Thanks to David Bau who provided the basis of the maze generator code"""
    
    LEFT    = 0
    UP      = 1
    RIGHT   = 2
    DOWN    = 3

    B_LEFT  = 0x04
    B_UP    = 0x02
    B_RIGHT = 0x01
    B_DOWN  = 0x08
    B_SET   = 0x10

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "columns",     "Columns per inch",         default = 1.0, min = 0.1, max = 3 ),
            DialogFloat( "rows",        "Rows per inch",            default = 1.0, min = 0.1, max = 3 ),
            DialogInt(   "seed",        "Random seed",              default = 1, min = 0, max = 10000.0, rbutton = True ),
            DialogBreak(),
            DialogFloat( "width",       "Width (x)",                default = width, units = "inches", min = 1.0, max = width ),
            DialogFloat( "length",      "Length (y)",               default = length, units = "inches", min = 1.0, max = length ),
            DialogFloat( "xOffset",     "Starting x location",      default = 0.0, units = "inches" ),
            DialogFloat( "yOffset",     "Starting y location",      default = 0.0, units = "inches" ),
        ]

    def generate( self, params ):
        random.seed( params.seed )
        
        cols = int( .9999999 + params.width * params.columns )
        rows = int( .9999999 + params.length * params.rows )
        maze = self.makeMaze( cols, rows )
        
        # turn the maze into chains
        xScale = params.width / (cols - 1)
        yScale = params.length / (rows - 1)
        dir = self.RIGHT
        x, y = 0, 0
        chain = []
        while True:
            chain.append( (params.xOffset + xScale * x, params.yOffset + yScale * y ) )
            edges = maze[ y * cols + x ]
            if dir == self.RIGHT:
                if edges & self.B_UP:       dir = self.UP
                elif edges & self.B_RIGHT:  dir = self.RIGHT
                elif edges & self.B_DOWN:   dir = self.DOWN
                else:                       dir = self.LEFT
            elif dir == self.UP:
                if edges & self.B_LEFT:     dir = self.LEFT
                elif edges & self.B_UP:     dir = self.UP
                elif edges & self.B_RIGHT:  dir = self.RIGHT
                else:                       dir = self.DOWN
            elif dir == self.LEFT:
                if edges & self.B_DOWN:     dir = self.DOWN
                elif edges & self.B_LEFT:   dir = self.LEFT
                elif edges & self.B_UP:     dir = self.UP
                else:                       dir = self.RIGHT
            else: # dir == self.DOWN
                if edges & self.B_RIGHT:    dir = self.RIGHT
                elif edges & self.B_DOWN:   dir = self.DOWN
                elif edges & self.B_LEFT:   dir = self.LEFT
                else:                       dir = self.UP
            
            if dir == self.UP:       y += 1
            elif dir == self.DOWN:   y -= 1
            elif dir == self.LEFT:   x -= 1
            else:                    x += 1
            
            if x < 0 or x > cols or y < 0 or y > rows:
                break
        return [chain]
    
    def makeMaze( self, w, h ):
        over = False
        maze = [0] * w * h
        path = random.sample([pos for pos in xrange(w * h) if maze[pos] == 0], 1)
        nextdir = -1
        while path:
            pos = path[-1]
            choices = [d for d in xrange(4) if self.canbuild(maze, w, h, pos, d, over)]
            if nextdir in choices and random.randint(0, 1) == 0: pass
            elif choices: nextdir = random.sample(choices, 1)[0]
            else: path.pop(); continue
            path.append( self.dobuild( maze, w, h, pos, nextdir, over ))
        # Mark the entry point
        maze[0] |= self.B_LEFT
        # Mark the exit point
        #maze[w * h - 1] |= self.B_RIGHT 
        return maze

    def dobuild( self, maze, w, h, pos, d, over):
        offset = (1, w, -1, -w)[d]
        maze[pos] |= 1 << d
        pos += offset
        while maze[pos]:
            maze[pos] ^= random.choice((0, 15))
            maze[pos] |= self.B_SET
            pos += offset
        maze[pos] |= 1 << (d ^ 2)
        return pos

    def canbuild( self, maze, w, h, pos, dir, over):
        if dir < 0: return False
        offset = (1, w, -1, -w)[dir]
        while not self.atedge( w, h, pos, dir ):
            pos += offset
            if maze[pos] == 0: return True
            if not over or not self.cancross(maze, pos, dir): return False
        return False

    def atedge( self, w, h, pos, dir ):
        if dir == self.LEFT:    return pos % w == w - 1
        if dir == self.UP:      return pos >= w * (h - 1)
        if dir == self.RIGHT:   return pos % w == 0
        if dir == self.DOWN:    return pos < w

    def cancross( self, maze, pos, dir ):
        return maze[pos] & 15 == (10, 5, 10, 5)[dir]




