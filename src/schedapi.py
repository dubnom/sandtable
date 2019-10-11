import socket
import json
from Sand import *

class schedapi(object):
    def __init__( self, hostName=SCHEDULER_HOST, portNumber=SCHEDULER_PORT ):
        self.hostName = hostName
        self.portNumber = portNumber
        self.BUFFER_SIZE = 512
        self._status = None

    def __enter__(self):
        return self

    def __exit__(self,e,t,tb):
        return False

    def command( self, command, data=None ):
        sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        sock.connect( (self.hostName, self.portNumber) )
        sock.sendall( json.dumps( (command,data) ))
        self._status = json.loads( sock.recv(self.BUFFER_SIZE))
        sock.close()
        del sock

    def demoOnce(self):
        self.command( "demoOnce" )

    def demoContinuous(self):
        self.command( "demoContinuous" )

    def demoHalt(self):
        self.command( "demoHalt" )

    def status(self):
        self.command( "status" )
        return self._status

    def restart(self):
        self.command( "restart" )

