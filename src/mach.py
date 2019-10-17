import socket
import json
from Sand import *

class mach:
    def __init__( self, hostName=MACH_HOST, portNumber=MACH_PORT ):
        self.hostName = hostName
        self.portNumber = portNumber
        self.BUFFER_SIZE = 512
        self.status = None

    def __enter__(self):
        return self

    def __exit__(self,e,t,tb):
        return False

    def command( self, string ):
        sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        sock.connect( (self.hostName, self.portNumber) )
        sock.sendall( bytes(json.dumps(string), encoding='utf-8'))
        v = sock.recv(self.BUFFER_SIZE)
        self.status = json.loads( v )
        sock.close()
        del sock
 
    def close( self ):
        pass
    
    def run( self, fileName, wait = False ):
        self.command( 'run %s %s' % (fileName,wait))

    def stop( self ):
        self.command( 'halt' )

    def restart( self ):
        self.command( 'restart' )

    def home( self ):
        self.command( 'home' )

    def getPosition( self ):
        self.command( 'status' )
        return self.status['pos']

    def getState( self ):
        self.command( 'status' )
        return self.status['state']
