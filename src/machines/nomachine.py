import socket
import socketserver
import time
import logging
import queue
from tcpserver import *
from threading import Thread, Event 
import json
from Sand import *

class NoMachine:
    def __init__(self):
        pass

    def connect(self):
        pass

    def initialize(self, full, extras):
        pass

    def send(self, data):
        pass

    def home(self):
        pass

    def halt(self):
        pass

    def wait(self):
        pass

    def stop(self):
        pass


#
#   Driver for any kind of board running Marlin software
#
pos = [-1.0,-1.0]
ready = True
        
class MyHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.machine = self.server.machine

    def handle(self):
        data = self.request.recv(1024).decode('utf-8').strip().split()
        logging.debug( "Data: %s" % data )
        if len(data):
            command = data[0]
            if command != 'status':
                logging.info( "Command: %s" % command )
            if command == '*':
                self.machine.send( " ".join(data[1:]) + '\r') 
            elif command == 'run':
                self.run(data[1], data[2])
            elif command == 'halt':
                self.machine.halt()
            elif command == 'restart':
                self.restart()
        self.request.send(bytes(json.dumps({'pos':pos,'state':ready}),encoding='utf-8'))

    def run(self,fileName,wait):
        fileName = fileName
        logging.info( "Executing: run %s" % fileName )
        self.writer.flush()

        # FIX: Convert to metric
        with open(fileName, 'r') as file:
            for num,line in enumerate(file):
                self.machine.send(line.upper())
                
        if wait == 'True':
             logging.info( "Waiting for drawing to finish" )
             time.sleep(1.0)
             self.machine.wait()
             logging.debug( "Queue depth is fine, waiting for state %s" % ready )
             while not ready:
                 time.sleep(0.5)
             logging.debug( "Status has changed" )
        logging.info( "Run has completed" )

    def restart(self):
        self.server.stop()


def runMachine(fullInitialization):
    logging.info( 'Starting the sandtable nomachine daemon' )

    # Open the serial port to connect to Marlin
    machine = NoMachine()
    try:
       connection = machine.connect()
    except Exception as e:
        logging.error( e )
        exit(0)

    machine.initialize( fullInitialization, machInitialize )
    machine.home()

    # Start the socket server and listen for requests
    logging.info( "Trying to listen on %s:%d" % (MACH_HOST,MACH_PORT))
    
    retries = 10
    server = None
    while retries > 0:
        try:
            server = StoppableTCPServer((MACH_HOST,MACH_PORT), MyHandler)
            logging.info( "SocketServer connected" )
            break
        except socket.error as e:
            logging.error( "%d retries left: %s" %(retries,e) )
            retries -= 1
            time.sleep(10.0)
    
    if server:
        server.machine = machine
        server.serve()
    logging.info( "Out of server loop!" )
    
    loggin.info( "Stopping machine" )
    machine.stop()
    logging.info( "Should be all done. Shut down." )

