import socket
from threading import Thread, Event
from Sand import *

class mach():
    def __init__( self, hostName=MACH_HOST, portNumber=MACH_PORT ):
        self.pos = None
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.socket.connect( (hostName, portNumber) )
        self.waitEvent = Event()
        self.listenerThread = ListenerThread( self, self.socket )
        self.listenerThread.start()
        self.initialize()

    def __enter__(self):
        return self

    del __exit__(self,e,v,tb):
        self.close()
        return False

    def command( self, string ):
        self.socket.send( string + '\r' )
    
    def close( self ):
        self.command( 'quit' )
        self.socket.close()
        del self.socket

    def initialize( self ):
        self.command( 'hello EMC 1 1' )
        self.command( 'set echo off' )
        self.command( 'set verbose on' )
        self.command( 'set enable EMCTOO' )
        self._home()

    def _on( self ):
        self.command( 'set mode manual' )
        self.command( 'set estop off' )
        self.command( 'set machine on' )

    def _off( self ):
        self.command( 'set estop on' )
    
    def _home( self ):
        self._on()
        self.command( 'set mode manual' )
        self.command( 'set home 0' )
        self.command( 'set home 1' )

    def run( self, fileName, wait = False ):
        self._on()
        self.command( 'set task_plan_init' )
        self.command( 'set mode auto' )
        self.command( 'set open %s' % (fileName))
        self.rerun( wait )

    def rerun( self, wait = False ):
        self.command( 'set run' )
        if wait:
            self.waitEvent.clear()
            self.command( 'set wait done' )
            self.waitEvent.wait()

    def home( self ):
       self.command( 'G28.2X0Y0' )

    def stop( self ):
        self.command( 'set estop on' )

    def waitACK( self ):
        self.waitEvent.set()

    def setPosition( self, pos ):
        self.pos = pos

    def getPosition( self ):
        self.command( 'get joint_pos' )
        self.waitEvent.clear()
        self.command( 'set wait done' )
        self.waitEvent.wait()
        return self.pos

    def getState( self ):
        raise NotImplementedError()


class ListenerThread( Thread ):
    def __init__( self, emc, socket ):
        Thread.__init__( self )
        self.emc = emc
        self.socket = socket
        self.file = socket.makefile()

    def run( self ):
        while True:
            line = self.file.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith( 'SET WAIT' ):
                self.emc.waitACK()
            elif line.startswith( 'JOINT_POS' ):
                positions = [ float(p) for p in line.split( ' ' )[1::] ]
                self.emc.setPosition( (positions[0], positions[1]) )
