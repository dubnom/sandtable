import sys
import serial
import socket
import socketserver
from tcpserver import *
from threading import Thread
import json
import time
import queue
import logging
from Sand import *

pos = [-1.0,-1.0]
state = [0,0]
        
class MyHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.writer = self.server.writer

    def handle(self):
        data = self.request.recv(1024).strip().split()
        logging.debug( "Data: %s" % data )
        if len(data):
            command = data[0]
            if command != 'status':
                logging.info( "Command: %s" % command )
            if command == '*':
                self.writer.send( " ".join(data[1:]) + '\n') 
            elif command == 'run':
                self.run(data[1],data[2])
            elif command == 'halt':
                self.halt()
            elif command == 'restart':
                self.restart()
            elif command == 'home':
                self.writer.send( '{"gc":"G28.2X0Y0"}\n' )
        self.request.send(json.dumps({'pos':pos,'state':state[0]}))

    def run(self,fileName,wait):
        fileName = fileName
        logging.info( "Executing: run %s" % fileName )
        self.writer.flush()
        with open(fileName, 'r') as file:
            for line in file:
                self.writer.send( '{"gc":"%s"}\n' % line.strip().replace(' ',''))
                
        if wait == 'True':
             logging.info( "Waiting for drawing to finish" )
             time.sleep(1.0)
             self.writer.wait()
             logging.debug( "Join has finished, waiting for queue depth %d" % state[1] )
             while state[1] < 28:
                 time.sleep(0.5)
             logging.debug( "Queue depth is fine, waiting for state %s" % state[0] )
             while not state[0]:
                 time.sleep(0.5)
             logging.debug( "Status has changed" )
        logging.info( "Run has completed" )

    def halt(self):
        logging.info( "Executing: halt" )
        self.writer.flush()

    def restart(self):
        self.server.stop()


class ReadThread(Thread):
    def __init__(self,ser):
        self.ser = ser
        super(ReadThread, self).__init__()

    def run(self):
        logging.info( "Reader thread active" )
        self.running = True
        while self.running:
            line = self.ser.readline().decode(encoding='utf-8').strip()
            if len(line):
                # Parse the lines for status here
                try:
                    data = json.loads(line)
                    # Parse status reports
                    if 'sr' in data:
                        status = data['sr']
                        if 'posx' in status:
                            pos[0] = status['posx']
                        if 'posy' in status:
                            pos[1] = status['posy']
                        if 'stat' in status:
                            logging.debug( "State: %d" % status['stat'] )
                            state[0] = status['stat'] in (1,3,4)
                    
                    # Parse queue reports
                    elif 'qr' in data:
                        queueDepth = data['qr']
                        state[1] = queueDepth
                        logging.debug( "QueueDepth: %d" % queueDepth )

                    # Parse responses
                    elif 'r' in data:
                        response = data['r']
                        logging.debug( "Response: %s" % response )

                    # Everything else
                    else:
                        logging.debug( "Received:",data )
                except ValueError:
                    logging.warning( "Couldn't parse: %s" % line )
        logging.info( "Reader thread exiting" )

    def stop(self):
        self.running = False


class Writer():
    def __init__(self,ser):
        self.queue = queue.Queue()
        self.writeThread = WriteThread(ser,self.queue)
        self.writeThread.start()

    def send(self,data):
        self.queue.put(data)

    def flush(self):
        logging.debug( "Flushing queue %d" % self.queue.qsize())
        while not self.queue.empty():
            self.queue.get()
            self.queue.task_done()
        logging.debug( "Done flushing queue" )

    def wait(self):
        self.queue.join()

    def stop(self):
        self.writeThread.stop()
        self.send('#Die')

class WriteThread(Thread):
    def __init__(self,ser,queue):
        self.ser = ser
        self.queue = queue
        super(WriteThread, self).__init__()

    def run(self):
        logging.info( "Writer thread active" )
        self.running = True
        while self.running:
            data = self.queue.get()
            while state[1] > 0 and state[1] < 6:
                time.sleep(.1)
            state[1] -= 1
            self.ser.write(bytes(data,encoding='utf-8'))
            self.queue.task_done()
        logging.info( "Writer thread exiting" )

    def stop(self):
        self.running = False
 

def runMachine(fullInitialization):
    logging.info( 'Starting the sandtable tinyg daemon' )

    # Open the serial port to connect to the TinyG
    try:
        ser = serial.Serial(MACHINE_PORT, baudrate=MACHINE_BAUD, rtscts=True, timeout=0.5)
    except Exception as e:
        logging.error( e )
        exit(0)

    # Start the read thread
    reader = ReadThread(ser)
    reader.start()

    # Create the writer
    writer = Writer(ser)

    # Initialize the board
    initialize = [
        {"rv":""},                      # Software version
        {"rb":""},                      # Software build
        {"ex":2},                       # Use CTS/RTS for flow control
        {"jv":4},                       # Line numbers
        {"qv":2},                       # Verbose queue reports
        {"gun":0},                      # Inches 
        {"sv":1},                       # Status reports (filtered)
    ]

    # Try not sending the initialization string
    if fullInitialization:
        initialize = initialize + machInitialize + ["reset"] + initialize

    # Add the homing commands
    initialize += [{"gc":"G28.2X0Y0"}]

    for i in initialize:
        writer.send( "\x18\n" if i=='reset' else json.dumps(i) + "\n" ) 
        time.sleep(6. if i=='reset' else .5)

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
        server.writer = writer
        server.serve()
    logging.info( "Out of server loop!" )
    
    logging.info( "Stopping writer" )
    writer.stop()
    logging.info( "Stopping reader" )
    reader.stop()
    logging.info( "Should be all done. Shut down." )
