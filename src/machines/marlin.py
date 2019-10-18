import serial
import logging
import queue
from threading import Thread
import json
from machine import Machine


class machiner(Machine):
    """ Driver for Marlin compatible controllers."""

    def initialize(self, params, fullInit):
        logging.info( 'Trying to connect to Marlin controller.' )

        # Open the serial port to connect to Marlin
        try:
            self.ser = serial.Serial(params['port'], baudrate=params['baud'], rtscts=True, timeout=0.5)
        except Exception as e:
            logging.error( e )
            exit(0)

        # Start the read thread
        self.reader = ReadThread(self, self.ser)
        self.reader.start()

        # Create the writer
        self.writer = WriteThread(self, self.ser)
        self.writer.start()

        # Initialize the board
        initialize = []
        if fullInit:
            logging.info( 'Full machine initialization.' )
            initialize += params['init'] + ['M500']

        for i in initialize:
            self.send( i ) 

        # Home the machine
        self.home()
        self.ready = True

    def home(self):
        self.send( 'G28.2X0Y0' )

    def halt(self):
        self.flush()
        self.send( "M18" )
        self.send( "M114" )
        
    def stop(self):
       self.writer.stop()
       self.reader.stop()
       self.ser.close()


class ReadThread(Thread):
    okCount = 0 

    def __init__(self, machine, ser):
        self.ser = ser
        super(ReadThread, self).__init__()

    def run(self):
        logging.info( "Read thread active" )
        self.running = True
        while self.running:
            line = self.ser.readline().decode(encoding='utf-8').strip()
            if len(line):
                logging.debug("<"+line)
                if line.startswith('ok'):
                    self.okCount += 1
        logging.info( "Read thread exiting" )

    def decrement(self):
        self.okCount -= 1

    def stop(self):
        self.running = False


class WriteThread(Thread):
    def __init__(self, machine, ser):
        self.ser = ser
        self.queue = machine.queue
        super(WriteThread, self).__init__()

    def run(self):
        logging.info( "Write thread active" )
        self.running = True
        while self.running:
            # FIX: Add conditional for controller readiness
            data = self.queue.get()
            self.ser.write(bytes(data+'\r',encoding='UTF-8'))
            self.queue.task_done()
        logging.info( "Write thread exiting" )

    def stop(self):
        self.running = False
 
