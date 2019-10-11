import opc
from LedsBase import LedsBase

# These parameters (LED_PARAMS) need to be defined in the machine's version file:
#   host    - Host name of the machine running the OPC server
#   port    - Port number of the OPC server
#
#  FIX: Mapping needs to be made more generic

class Leds(LedsBase):
    """Communicate with an OPC compatible lighting system"""
    def __init__( self, rows, cols, mapping, params ):
        self.mapping = mapping
        self.host    = params['host']
        self.port    = params['port']
        LedsBase.__init__(self, rows, cols )

    def connect( self ):
        self.client = opc.Client( '%s:%d' % (host, port))
        self.mapping = range(0,60)+range(60,90)+range(149,89,-1)+range(179,149,-1)

    def refresh( self ):
        self.client.put_pixels( map(lambda i:self.leds[i],self.mapping ) if self.mapping else self.leds )

    def disconnect( self ):
        self.client.disconnect()
        del self.client
