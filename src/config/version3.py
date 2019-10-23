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

MACHINE             = "tinyg"
MACHINE_UNITS       = "inches"
MACHINE_FEED        = 400.0     # Inches per minute
MACHINE_ACCEL       = 30.0      # Inches per second squared

MACHINE_PARAMS = {
    'port':     "/dev/ttyUSB0",
    'baud':     115200,
    'init': [
        {"mt":2},                       # Motor enable timeout
        {"st":0},                       # Switch polarity (NO)

        # X-axis motor pair
        {"1ma":0},                      # Axis number
        {"1sa":1.8},
        {"1tr":1.5748},                 # Inches per rotation
        {"1mi":8},
        {"1pm":2},

        {"3ma":0},                      # Axis number
        {"3sa":1.8},
        {"3tr":1.5748},                 # Inches per rotation
        {"3mi":8},
        {"3po":1},                      # Motor polarity
        {"3pm":2},

        # Y-axis motor pair
        {"2ma":1},                      # Axis number
        {"2sa":1.8},
        {"2tr":1.5748},                 # Inches per rotation
        {"2mi":8},
        {"2pm":2},

        {"4ma":1},                      # Axis number
        {"4sa":1.8},
        {"4tr":1.5748},                 # Inches per rotation
        {"4mi":8},
        {"4po":1},                      # Motor polarity
        {"4pm":2},

        {"xsn":1},                      # Min switch (home)
        {"xsx":0},                      # Max switch (none)
        {"xtm":TABLE_WIDTH},            # x travel max
        {"xvm":400},                    # Max velocity
        {"xfr":400},                    # Max feed rate
        {"xjm":120},                    # x jerk
        {"xjd":.1},

        {"xjh":40},                     # X Homing parameters
        {"xsv":50},
        {"xlb":.15},
        {"xzb":.15},
        {"xlv":50},

        {"ysn":1},                      # Min switch (home)
        {"ysx":0},                      # Max switch (none)
        {"ytm":TABLE_LENGTH},           # y travel max
        {"yvm":400},                    # Max velocity
        {"yfr":400},                    # Max feed rate
        {"yjm":120},                    # y jerk
        {"yjd":.1},

        {"yjh":40},                     # Y Homing parameters
        {"ysv":50},
        {"ylb":.2},
        {"yzb":.2},
        {"ylv":50},
    ]
} 

