# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

CACHE_ENABLE        = True
IMAGE_TYPE          = 'Realistic'
BALL_SIZE           = 0.75      # Diameter of ball
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

TABLE_UNITS         = "inches"
TABLE_WIDTH         = 30.0
TABLE_LENGTH        = 20.0

LED_DRIVER          = "LedsDS"
LED_PARAMS          = None
LED_COLUMNS         = 172 
LED_ROWS            = 116
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "marlin"
MACHINE_UNITS       = "mm"
MACHINE_FEED        = 100.0
MACHINE_ACCEL       = 100.0

MACHINE_PARAMS = {
    'port': "/dev/ttyACM0",
    'baud': 115200,
    'init': [
        "M92 X%.8g" % (200/500),   # Steps/mm
        "M92 Y%.8g" % (200/500),   #
        "M203 X%g" % 100,          # Max feed mm / second
        "M203 Y%g" % 100,          # Max feed mm / second
        "M211 S0",                 # Disable software endstops
        ]
}
