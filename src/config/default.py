# Constants
global TABLE_FEED, BALL_SIZE

HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

TABLE_UNITS         = "inches"
TABLE_WIDTH         = 30.0
TABLE_LENGTH        = 30.0
TABLE_FEED          = 40.0      # inches per minute
TABLE_ACCEL         = 40.0      # inches per second squared
BALL_SIZE           = 0.75      # Diameter of ball

LED_DRIVER          = "LedsDS"
LED_PARAMS          = None
LED_COLUMNS         = 172 
LED_ROWS            = 116
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "nomachine"
MACHINE_UNITS       = "inches"
MACHINE_FEED        = 1.
MACHINE_PARAMS      = {}

