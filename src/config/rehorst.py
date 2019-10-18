# Constants
global TABLE_FEED, BALL_SIZE

HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

TABLE_WIDTH         = 748.0 / 25.4  # Width in inches (converted from mm)
TABLE_LENGTH        = 1565.0 / 25.4 # Length in inches (converted from mm)
TABLE_FEED          = 400.0         # Inches per minute
TABLE_ACCEL         = 30.0          # Inches per second squared
BALL_SIZE           = 0.75          # Diameter of ball (inches)

LED_DRIVER          = "LedsDS"
LED_PARAMS          = None
LED_COLUMNS         = 172 
LED_ROWS            = 116
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "smoothie"
MACHINE_UNITS       = "inches"

MACHINE_PARAMS = {
    'port': "/dev/ttyACM0",
    'baud': 115200,
    'init': [],
}

