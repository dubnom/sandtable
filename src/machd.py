#!/usr/bin/python3
import logging
import socket
import json
import socketserver
from importlib import import_module
from tcpserver import *
from threading import Thread, Event 
from Sand import *


class MyHandler(socketserver.BaseRequestHandler):
    pos = [-1.0,-1.0]
    ready = True

    def setup(self):
        self.machine = self.server.machine

    def handle(self):
        data = json.loads( self.request.recv(1024).decode('utf-8')).strip().split()
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

        state = {'pos':self.pos, 'state':self.ready}
        self.request.send(bytes(json.dumps(state),encoding='utf-8'))

    def run(self,fileName,wait):
        fileName = fileName
        logging.info( "Executing: run %s" % fileName )
        self.machine.flush()

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


def runMachine(machiner, params, fullInitialization):
    logging.info( 'Starting the sandtable machine daemon' )

    # Connect to the machine
    try:
        machine = machiner( params, fullInitialization )
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
    logging.info( "Stopping machine" )
    machine.stop()
    logging.info( "Should be all done. Shut down." )


def main():
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
    machine_module = import_module('machines.%s' % MACHINE)
    machiner = machine_module.machiner

    # Check settings update file
    fullInitialization = True
    try:
        with open(VER_FILE,'rb') as f:
            oldVersion = pickle.load(f)
        if oldVersion == MACHINE_PARAMS:
            fullInitialization = False
    except Exception as e:
        logging.error(e)

    if fullInitialization:
        with open(VER_FILE,'wb') as f:
            pickle.dump(MACHINE_PARAMS, f, protocol=4)

    runMachine(machiner, MACHINE_PARAMS, fullInitialization)


main()
exit(1)
