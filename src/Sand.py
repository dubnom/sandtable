# List of supported drawing classes
sandables = [
        "Sun","Spiral", "Text",
        "Waves", "Lissajous", "Grid",
        "Maze", "Snowflake", "Spirograph",
        "Wood", "Dragon", "Hilbert",
        "Clipart", "Checkers", "Man",
        "Lorenz", "Shingles", "Rose",
        "Star", "Fermat", "Move",
        "Lindenmayer", "Harmonograph", "Func3d",
        "Rocks", "SpiralArms", "Sines",
        "Picture", "WebPic", "RandomDraw",
        "Bulbs", "Engine", "ESpiral",
        "Grass",
        ]

todo = [ "Tree", "Celtic", "LOGO", "GreekKey", "CropCircle", "Propogation", ]

# List of LED patterns
ledPatterns = [
        "Off", "On", "Rainbow",
        "Pastel", "Marquee", "Kaleidoscope",
        "Orbit", "Distortion", "LightBall",
        "OneColor", "LightHouse","Dots",
        "Holidays", "Fire", "Ocean",
        "Clock", "Heartbeat", "RandomLights",
        "Balloon","Sky","Emitter",
        ]

# Import machine specific constants. This is done through a hostmap file
# located in the machines subdirectory.
import platform 
HOST_NAME = platform.node()
from machines.hostmap import hostmap
exec "from machines.%s import *" % hostmap[HOST_NAME]

# Constants
SERVER_LOG          = "/var/log/sandtable.log"

ROOT_DIRECTORY      = "/var/www/sandtable"
DATA_PATH           = "data/"
PICTURE_PATH        = "pictures/"
CLIPART_PATH        = 'clipart'
MOVIE_SCRIPT_PATH   = "scripts/"
MOVIE_OUTPUT_PATH   = "movies/"
STORE_PATH          = "store/"
SOURCE_PATH         = "src/"
MACH_PATH           = "%smachines/" % SOURCE_PATH
TMP_PATH            = "/tmp/"

CONFIG_FILE         = "%sconfig.pkl" % DATA_PATH

MACH_HOST           = 'localhost'
MACH_PORT           = 5007
MACH_LOG            = "/var/log/machd.log"
GCODE_FILE          = "%sgcode.ngc" % DATA_PATH

VER_FILE            = "%smach.py" % DATA_PATH
MACH_FILE           = "%s%s.py" % (MACH_PATH, hostmap[HOST_NAME])

IMAGE_FILE          = "%spath.png" % DATA_PATH
IMAGE_WIDTH         = 400
IMAGE_HEIGHT        = int(IMAGE_WIDTH * (TABLE_LENGTH / TABLE_WIDTH))

CACHE_FILE          = "%ssandtable.pkl" % TMP_PATH

HISTORY_COUNT       = 20

MOVIE_STATUS_LOG    = "%smovie_progress" % TMP_PATH
MOVIE_STATUS_FILE   = "%smovie_status.pkl" % TMP_PATH
MOVIE_WIDTH         = 864 
MOVIE_HEIGHT        = 576

LED_HOST            = 'localhost'
LED_PORT            = 5008
LED_LOG             = "/var/log/ledaemon.log"

SCHEDULER_HOST      = 'localhost'
SCHEDULER_PORT      = 5009
SCHEDULER_LOG       = "/var/log/scheduler.log"

# Configurable "constants"
import cPickle as pickle

class Config(object):
    imgType     = True
    maxFeed     = 600
    ballSize    = .75
    cache       = True
    cgiDebug    = True
    scheduler   = True
    
def LoadConfig():
    try:
        cfg = pickle.load( file( CONFIG_FILE, 'rb' ))
    except:
        cfg = Config()
    return cfg

def SaveConfig(cfg):
    pickle.dump( cfg, file( CONFIG_FILE, 'wb' ))

LoadConfig()

class Sandable(object):
    editor = []
    def generate( self, params ):
        return []

class Ledable(object):
    editor = []
    def generator( self, leds, cols, rows, params ):
        pass

def sandableFactory( sandable ):
    if sandable in sandables:
        exec "import draw.%s" % sandable
        exec "sand = draw.%s.%s( %f, %f )" % (sandable, sandable, TABLE_WIDTH, TABLE_LENGTH )
        return sand
    else:
        return None

class SandException( BaseException ):
    pass 