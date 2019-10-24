# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

CACHE_ENABLE        = True
IMAGE_TYPE          = 'Realistic'
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

BALL_SIZE           = 0.75
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
MACHINE_FEED        = 60 * 50.0     # mm/minute
MACHINE_ACCEL       = 3000.0

MACHINE_PARAMS = {
    'port': "/dev/ttyACM0",
    'baud': 115200,
    'init': [
        "M92 X%.8g" % (16*200/50),  # microsteps*StepsPerRotation/mm
        "M92 Y%.8g" % (16*200/50),  #
        "M203 X%g" % 150,           # Max feed mm / second
        "M203 Y%g" % 150,           # Max feed mm / second
        "M211 S0",                  # Disable software endstops
        ]
}
