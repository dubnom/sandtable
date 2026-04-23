# Constants
HOST_ADDR           = '0.0.0.0'
HOST_PORT           = 80

CACHE_ENABLE        = True
IMAGE_TYPE          = 'Realistic'
BALL_SIZE           = 0.75          # Diameter of ball
LOGGING_LEVEL       = "debug"
SCHEDULER_ENABLE    = True

TABLE_UNITS         = "inches"
TABLE_WIDTH         = 30
TABLE_LENGTH        = 20

LED_DRIVER          = "LedsDS"
LED_PARAMS          = None
LED_COLUMNS         = 172 
LED_ROWS            = 116
LED_PERIOD          = 1.0 / 45.0
LED_OFFSETS         = [ (1,2), (4,4) ]
LED_MAPPING         = None

MACHINE             = "fluidnc"
MACHINE_UNITS       = "mm"
MACHINE_FEED        = 1000.0         # Inches? per minute
MACHINE_ACCEL       = 50.0          # Inches? per second squared


MACHINE_PARAMS = {
    'port': "/dev/ttyUSB0",
    'baud': 115200,
    'init': [
        '$Sta/SSID=quokka',
        '$Sta/Password=$mokecheddadaassgetta]',
        '$Sta/IPMode=DHCP',
        '$STA/SSDP/Enable=true',
        '$Hostname=fluidnc',
        ]
}

