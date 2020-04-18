# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

CACHE_ENABLE        = True
IMAGE_TYPE          = 'Realistic'
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

BALL_SIZE           = 12.7
TABLE_UNITS         = "mm"
TABLE_WIDTH         = 990.0
TABLE_LENGTH        = 495.0

LED_DRIVER          = "LedsDS"
LED_PARAMS          = None
LED_COLUMNS         = 172 
LED_ROWS            = 116
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "marlin"
MACHINE_UNITS       = "mm"
MACHINE_FEED        = 60 * 66.6     # mm/minute
MACHINE_ACCEL       = 200.0

MACHINE_PARAMS = {
    'port': "/dev/ttyUSB0",
    'baud': 115200,
    'init': [
        "M92 X%.8g" % 80.5,  # microsteps*StepsPerRotation/mm
        "M92 Y%.8g" % 80.5,  #
        "M203 X%g" % 67,     # Max feed mm / second
        "M203 Y%g" % 67,     # Max feed mm / second
        "M211 S0",           # Disable software endstops
        ]
}
