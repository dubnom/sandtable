# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

CACHE_ENABLE        = True
IMAGE_TYPE          = 'Realistic'
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

BALL_SIZE           = 0.625 * 2.54
TABLE_UNITS         = "cm"
TABLE_WIDTH         = 60.0
TABLE_LENGTH        = 60.0

LED_DRIVER          = "LedsDS"
LED_PARAMS          = { 'brightness': .5 }
LED_COLUMNS         = 72 
LED_ROWS            = 72
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "grbl"
MACHINE_UNITS       = "mm"
MACHINE_FEED        = 8000          # mm/minute
MACHINE_ACCEL       = 1500          # mm/sec^2

MACHINE_PARAMS = {
    'port': "/dev/ttyUSB0",
    'baud': 115200,
    'init': [
        "$10=2",                        # Only report the work position
        "$110=%g" % MACHINE_FEED,       # X axis mm/minute
        "$111=%g" % MACHINE_FEED,       # Y axis mm/minute
        "$120=%g" % MACHINE_ACCEL,      # X axis mm/sec^2
        "$121=%g" % MACHINE_ACCEL,      # Y axis mm/sec^2
        "$130=%g" % (TABLE_WIDTH*10),   # X axis max travel mm
        "$131=%g" % (TABLE_LENGTH*10),  # Y axis max travel mm
        "$132=10",                      # Z axis max travel mm (bogus timeout number)
        "$23=3",                        # Invert the homing to try for 0,0
        "$27=4",                        # Homing pull-off mm
        "$21=0",                        # Hardlimits FIX: SHOULD BE TRUE
        "$22=0",                        # Homing FIX: SHOULD BE TRUE

        #"M92 X%.8g" % (16*200/50),  # microsteps*StepsPerRotation/mm
        #"M92 Y%.8g" % (16*200/50),  #
        #"M203 X%g" % 150,           # Max feed mm / second
        #"M203 Y%g" % 150,           # Max feed mm / second
        #"M211 S0",                  # Disable software endstops
        ]
}
