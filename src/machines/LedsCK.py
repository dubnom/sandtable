from array import array
from socket import socket, AF_INET, SOCK_DGRAM
from LedsBase import LedsBase

# These parameters (LED_PARAMS) need to be defined in the machine's version file:
#   addr - (host,port) host and port number of the Color Kinetics server
#


class Leds(LedsBase):
    """Communicate with a Color Kinetics lighting system"""

    def __init__(self, rows, cols, mapping, params):
        self.mapping = mapping
        self.addr = params['addr']
        LedsBase.__init__(self, rows, cols)

    def connect(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def refresh(self):
        colors = [0x04, 0x01, 0xdc, 0x4a, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00]
        colors += [self.leds[i] for i in self.mapping] if self.mapping else self.leds
        colors += [0x00, 0x00]
        data = array('B', colors)
        self.socket.sendto(data.tostring(), self.addr)

    def disconnect(self):
        self.socket.close()
        del self.socket
