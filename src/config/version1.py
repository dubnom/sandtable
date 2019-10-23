# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

CACHE_ENABLE        = True
IMAGE_TYPE          = 'Realistic'
BALL_SIZE           = 0.75      # Diameter of ball
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

TABLE_UNITS         = "inches"
TABLE_WIDTH         = 36.0
TABLE_LENGTH        = 16.0

LED_DRIVER          = "LedsOPC"
LED_PARAMS          = {'host':'localhost','port':7890}
LED_COLUMNS         = 60 
LED_ROWS            = 30
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = list(range(0,60))+list(range(60,90))+list(range(149,89,-1))+list(range(179,149,-1))

MACHINE             = "tinyg"
MACHINE_UNITS       = "inches"
MACHINE_FEED        = 600.0     # Inches per minute
MACHINE_ACCEL       = 30.0      # Inches per second squared

MACHINE_PARAMS = {
    'port': "/dev/ttyUSB0",
    'baud': 115200,
    'init': [
        {"1tr":2.0},                    # Inches per rotation
        {"1po":0},                      # Motor polarity
        {"1sa":1.8,"1pm":1,"1mi":8},
        {"2tr":3.2},                    # Inches per rotation
        {"2po":1},                      # Motor polarity
        {"2sa":1.8,"2pm":1,"2mi":8},

        {"xsn":1},                      # Min switch (home)
        {"xsx":0},                      # Max switch (none)
        {"xtm":TABLE_WIDTH},            # x travel max
        {"xvm":600},                    # Max velocity
        {"xfr":600},                    # Max feed rate
        {"xjr":50000000},               # x jerk

        {"xjh":40000000},               # X Homing parameters
        {"xsv":50},
        {"xlb":.15},
        {"xzb":.15},
        {"xlv":50},

        {"ysn":1},                      # Min switch (home)
        {"ysx":0},                      # Max switch (none)
        {"ytm":TABLE_LENGTH},           # y travel max
        {"yvm":600},                    # Max velocity
        {"yfr":600},                    # Max feed rate
        {"yjr":50000000},               # y jerk

        {"yjh":40000000},               # Y Homing parameters
        {"ysv":50},
        {"ylb":.2},
        {"yzb":.2},
        {"ylv":50},
    ]
}


