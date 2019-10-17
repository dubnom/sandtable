import socket
import socketserver
import time
import logging
import queue
from tcpserver import *
from threading import Thread, Event 
import json
from Sand import *

class Machine:
    """ Base class for communicating with a CNC controller.
    
        Subclasses must implement:
            initialize - connect and initialize the actual machine (through serial,
                         API, etc.) it expects:
                             machInitialize - settings like motor mapping, acceleration, etc.
                             This initialization should be sent if not None.
            home - home the machine.
            halt - halt the machine.
            stop - disconnect from the machine.
    """

    def __init__(self, fullInitialization, machInitialize ):
        # FIX: Add machine specific parameters as a dictionary
        self.queue = queue.Queue()
        self.initialize( machInitialize)

    def send(self, data):
        self.queue.put(data)

    def home(self):
        pass

    def halt(self):
        pass

    def wait(self):
        self.queue.join()

    def flush(self):
        while not self.queue.empty():
            self.queue.get()
            self.queue.task_done()

    def stop(self):
        pass


class NoMachine(Machine):
    def initialize(self, machInitialize):
        self.writeThread = NoWriteThread(self)
        self.writeThread.start()
        self.stopFlag = Event()

    def stop(self):
        self.stopFlag.set()

class NoWriteThread(Thread):
    def __init__(self,machine):
        self.queue = machine.queue
        super(WriteThread, self).__init__()

    def run(self):
        self.running = True
        while self.running:
            data = self.queue.get()
            logging.info( "Writing %s" % data )
            self.queue.task_done()

    def stop(self):
        self.running = False



#
#   Driver for any kind of board running Marlin software
#
        
class MyHandler(socketserver.BaseRequestHandler):
    pos = [-1.0,-1.0]
    ready = True

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
        self.request.sendall(bytes(json.dumps({'pos':self.pos,'state':self.ready}),encoding='utf-8'))

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
             logging.debug( "Queue depth is fine, waiting for state %s" % self.ready )
             while not self.ready:
                 time.sleep(0.5)
             logging.debug( "Status has changed" )
        logging.info( "Run has completed" )

    def restart(self):
        self.server.stop()


def runMachine(fullInitialization):
    logging.info( 'Starting the sandtable machine daemon' )

    # Connect to the machine
    try:
        machine = Machine( machInitialize if fullInitialization else None )
    except Exception as e:
        logging.error( e )
        exit(0)

    # Home the machine so it is in a known state
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
    
    # If SocketServer connected, then start listening and dispatching commands to the machine
    if server:
        server.machine = machine
        server.serve()
    logging.info( "Out of server loop!" )
    
    # Close everything down
    loggin.info( "Stopping machine" )
    machine.stop()
    logging.info( "Should be all done. Shut down." )

