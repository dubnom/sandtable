# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 443
ADHOC_SSL           = True
SERVER_DEBUG        = False

CACHE_ENABLE        = True
IMAGE_TYPE          = 'ClippedLine'   # 'Realistic', 'ClippedLine' or 'Line'
BALL_SIZE           = 0.75          # Diameter of ball
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

TABLE_UNITS         = "inches"
TABLE_WIDTH         = 38
TABLE_LENGTH        = 17

LED_DRIVER          = "LedsNeo"
LED_PARAMS          = None
LED_COLUMNS         = 172 
LED_ROWS            = 116
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "fluidnc"
MACHINE_UNITS       = "mm"
MACHINE_FEED        = 3000.0         # Inches? per minute
MACHINE_ACCEL       = 100.0          # Inches? per second squared


MACHINE_PARAMS = {
    'port': "/dev/ttyUSB0",
    'baud': 115200,
    'init': [
        ]
}

