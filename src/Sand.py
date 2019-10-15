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

# Constants
SERVER_LOG          = "/var/log/sandtable.log"

ROOT_DIRECTORY      = "/var/www/sandtable"
DATA_PATH           = "data/"
PICTURE_PATH        = "pictures/"
CLIPART_PATH        = "clipart"
MOVIE_SCRIPT_PATH   = "scripts/"
MOVIE_OUTPUT_PATH   = "movies/"
STORE_PATH          = "store/"
SOURCE_PATH         = "src/"
CONFIG_PATH         = "config"
TMP_PATH            = "/tmp/"

CONFIG_FILE         = "%sconfig.pkl" % DATA_PATH

MACH_HOST           = 'localhost'
MACH_PORT           = 5007
MACH_LOG            = "/var/log/machd.log"
GCODE_FILE          = "%sgcode.ngc" % DATA_PATH

VER_FILE            = "%smachine.py" % DATA_PATH

IMAGE_FILE          = "%spath.png" % DATA_PATH
IMAGE_WIDTH         = 400

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

# Import machine specific configuration. This is done through a hostmap file
# located in the machines subdirectory.
import platform 
HOST_NAME = platform.node()
exec("from %s.hostmap import hostmap" % CONFIG_PATH)
exec("from %s.%s import *" % (CONFIG_PATH, hostmap[HOST_NAME]))

IMAGE_HEIGHT        = int(IMAGE_WIDTH * (TABLE_LENGTH / TABLE_WIDTH))


# Configurable "constants"
import pickle as pickle

class Config():
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

class Sandable():
    editor = []
    def generate( self, params ):
        return []

class Ledable():
    editor = []
    def generator( self, leds, cols, rows, params ):
        pass

def sandableFactory( sandable ):
    globs = globals()
    locs = {}
    
    if sandable in sandables:
        exec("import draw.%s" % sandable, globs, locs)
        exec("sand = draw.%s.%s( %f, %f )" % (sandable, sandable, TABLE_WIDTH, TABLE_LENGTH ), globs, locs)
        return locs['sand']
    else:
        return None

class SandException( BaseException ):
    pass 
