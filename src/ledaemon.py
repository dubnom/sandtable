#!/usr/bin/python
import os
import pickle
import time
import logging
import json
import socket
import SocketServer
from tcpserver import *
from threading import Thread

from Sand import *
from LedsBase import LedsBase
 
# The specific LED driver is specified in the machine configuration
exec "import %s as Leds" % LED_DRIVER

class startupPattern( Ledable ):
    def __init__( self, cols, rows ):
        self.editor = []

    def generator( self, leds, cols, rows, params ):
        revCount = 120
        for rev in range(revCount):
            leds.set( 0, leds.HSB( 720.0*rev/revCount, 100, 50 * rev / revCount), end = len( leds.leds)-1)
            yield True
        yield False


class LedThread(Thread):
    def __init__(self):
        super(LedThread, self).__init__()
        self.leds = Leds.Leds( LED_ROWS, LED_COLUMNS, LED_MAPPING, LED_PARAMS ) 
        self.leds.refresh()
        self.setPattern( startupPattern( LED_COLUMNS, LED_ROWS ), None )

    def run(self):
        self.running = True
        logging.info( "LedThread active" )
        while self.running:
            if self.generator:
                try:
                    if self.generator.next():
                        self.leds.refresh()
                except (GeneratorExit, StopIteration):
                    # Generator has finished, turn off the lights
                    logging.info( "Pattern has finished" )
                    self.leds.clear()
                    self.leds.refresh()
                    self.generator = None
            time.sleep( LED_PERIOD )
        self.leds.close()
        logging.info( "LedThread exiting" )

    def setPattern(self,pattern,params):
        logging.info( "Switching to pattern: %s" % pattern )
        self.pattern = type(pattern).__name__
        self.generator = pattern.generator( self.leds, LED_COLUMNS, LED_ROWS, params )

    def stop(self):
        self.running = False

    def status(self):
        return { 'running': self.generator != None, 'pattern':self.pattern }


class MyHandler(SocketServer.BaseRequestHandler):
    def setup(self):
        self.ledThread = self.server.ledThread

    def handle(self):
        req = self.request.recv(10*1024)
        cmd, pattern, params = pickle.loads( req )
        if cmd == 'pattern':
            self.ledThread.setPattern( pattern, params )
            logging.info( "Request: %s %s %s" % (cmd, pattern, params ))
        elif cmd == 'status':
            pass
        elif cmd == 'restart':
            self.server.stop()
        self.request.send(json.dumps(self.ledThread.status()))

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)
    logging.info( 'Starting the SandTable ledaemon' )
    
    ledThread = LedThread()
    ledThread.start()

    # Start the socket server and listen for requests
    # Retry logic has been implemented because sometimes sockets don't release quickly
    # FIX: The retry logic should be moved to the socket server itself
    logging.info( "Trying to listen on %s:%d" % (LED_HOST, LED_PORT ))
    retries = 10
    server = None
    while retries > 0:
        try:
            server = StoppableTCPServer((LED_HOST,LED_PORT), MyHandler)
            logging.info( "SocketServer connected" )
            break
        except socket.error as e:
            logging.error( "%d retries left: %s" %(retries,e) )
            retries -= 1
            time.sleep(10.0)
    if server:
        server.ledThread = ledThread
        server.serve()
    logging.info( "Out of server loop!" )

    ledThread.stop()

    exit(1)
