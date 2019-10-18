# Constants
global TABLE_FEED, BALL_SIZE

HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

TABLE_UNITS         = "inches"
TABLE_WIDTH         = 30.0
TABLE_LENGTH        = 20.0
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

MACHINE             = "marlin"
MACHINE_UNITS       = "mm"

MACHINE_PARAMS = {
    'port': "/dev/ttyACM0",
    'baud': 115200,
    'init': [
        "M92 X%.8g" % (200*10/25.4),  # 200 Steps/rev * 10 rev/inch / (25.4mm/inch)
        "M92 Y%.8g" % (200*10/25.4),  #
        "M211 S0",                    # Disable software endstops
        ]
}
