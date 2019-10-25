import serial
import logging
from threading import Thread
import re
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
        fullInit = True     # FIX: Board doesn't seem to remember anything
        if fullInit:
            logging.info( 'Full machine initialization.' )
            initialize += params['init'] + ['M500','G1 Z1','M114']

        for i in initialize:
            self.send( i ) 

        # Home the machine
        self.home()
        self.ready = True

    def run(self, chains, units, feed):
        self.ready = False
        self.send( 'M17' )
        self.send( 'G1 F%g' % feed )
        self.send( 'G1 Z0' )
        self.count = 0
        for chain in chains:
            for point in chain:
                s =  'G1 X%g Y%g' % (round(point[0],1), round(point[1],1))
                self.send( s )
                self.count += 1
                if self.count % 10 == 0:
                    self.send( "M114" )
        self.send( 'G1 Z1' )
        self.send( 'M18' )
        self.send( "M114" )

    def home(self):
        pass
        # FIX: NEED LIMIT SWITCHES
        #self.send( 'G28.2X0Y0' )

    def halt(self):
        self.flush()
        self.send( 'G1 Z1' )
        self.send( "M18" )
        self.send( "M114" )
        
    def stop(self):
       self.writer.stop()
       self.reader.stop()
       self.ser.close()


class ReadThread(Thread):
    def __init__(self, machine, ser):
        self.machine = machine
        self.ser = ser
        super(ReadThread, self).__init__()

    def run(self):
        logging.info( "Read thread active" )
        reStatus = re.compile( '^X:([\d.-]+) Y:([\d.-]+) Z:([\d.-]+) E:([\d.-]+) Count X:([\d.-]+) Y:([\d.-]+) Z:([\d.-]+)$' )
        self.running = True
        while self.running:
            line = self.ser.readline().decode(encoding='utf-8').strip()
            if len(line):
                logging.debug("<"+line)
                if line.startswith('ok'):
                    pass
                else:
                    match = reStatus.match(line)
                    if match:
                        self.machine.pos[0] = float(match.groups()[0])
                        self.machine.pos[1] = float(match.groups()[1])
                        # Use the Z axis as a way of determining that a drawing has ended (0-busy, 1-ready)
                        self.machine.ready = float(match.groups()[2]) > .5

        logging.info( "Read thread exiting" )

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
            logging.debug('%d %s' % (self.queue.qsize(), data))
            self.ser.write(bytes(data+'\r',encoding='UTF-8'))
            self.queue.task_done()
        logging.info( "Write thread exiting" )

    def stop(self):
        self.running = False
 
