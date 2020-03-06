import serial
from threading import Thread
import logging
from queue import Empty
import re
import time
from machine import Machine


POSITION_POLL_FREQ = 30     # Poll for status every 30 instructions


class machiner(Machine):
    """Driver for GRBL compatible controllers."""

    def initialize(self, params, fullInit):
        logging.info('Trying to connect to GRBL controller.')

        # Open the serial port to connect to Smoothie
        try:
            self.ser = serial.Serial(params['port'], baudrate=params['baud'], rtscts=True, timeout=0.5)
        except Exception as e:
            logging.error(e)
            exit(0)

        # Initialize the queue depth tracker
        self.queueDepth = 0

        # Start the read thread
        self.reader = ReadThread(self, self.ser)
        self.reader.start()

        # Create the writer
        self.writer = WriteThread(self, self.ser)
        self.writer.start()

        # Initialize the board
        initialize = []
        if fullInit:
            initialize += params['init']

        logging.info('Waiting for Grbl to be ready')
        while not self.reader.ready:
            time.sleep(.2)
        logging.info('Grbl ready')
            
        for i in initialize:
            self.send(i)

    def run(self, chains, units, feed):
        if units == 'inches':
            rounding = 2
            self.send('G20')
        else:
            rounding = 0
            self.send('G21')
        self.send('F%g' % feed)
        for chain in chains:
            for point in chain:
                s = 'G1X%gY%g' % (round(point[0], rounding), round(point[1], rounding))
                self.send(s)
        self.send('M2')

    def home(self):
        self.send('$X')
        self.send('G54')
        self.send('G92.1')
        self.send('G91')
        self.send('G0X%gY%g' % (-10*60, -10*60))    # FIX: Remove hardcoded values
        self.send('G0X5Y5')                         # FIX: hardcoded, backoff
        self.send('G90')
        self.send('G92 X0 Y0 Z0')
        #time.sleep(10.)     # FIX: This sucks
        #self.send(chr(24))
        #self.send('$X')

    def halt(self):
        self.flush()
        #self.send("abort")

    def stop(self):
        self.writer.stop()
        self.reader.stop()
        self.ser.close()


class ReadThread(Thread):
    def __init__(self, machine, ser):
        self.machine = machine
        self.ser = ser
        self.ready = False
        super(ReadThread, self).__init__()

    def run(self):
        reStatus = re.compile(r'^<(Idle|Run),WPos:([\d.-]+),([\d.-]+),([\d.-]+)(.*)>$')

        logging.info("Read thread active")
        self.running = True
        while self.running:
            line = self.ser.readline().decode(encoding='utf-8').strip()
            if len(line):
                # Parse the lines for status here
                if line.startswith('Grbl'):
                    self.ready = True
                else:
                    try:
                        # Parse status reports
                        match = reStatus.match(line)
                        if match:
                            logging.warning('Matched %s' % str(match.groups()))
                            status = match.groups()[0]
                            self.machine.pos[0] = float(match.groups()[1])
                            self.machine.pos[1] = float(match.groups()[2])
                            self.machine.ready = status == 'Idle'

                        # Parse responses
                        elif line == 'ok':
                            self.machine.queueDepth -= 1
                            logging.warning( "ok: %4d" % self.machine.queueDepth )

                        elif line.startswith('error'):
                            self.machine.queueDepth -= 1
                            logging.error( "error: %04d %s" % line )

                        # Everything else
                        else:
                            logging.warning("Received: %4d %s" % (self.machine.queueDepth, line))
                    except (ValueError, TypeError):
                        logging.warning("Couldn't parse: %s" % line)
        logging.info("Read thread exiting")

    def stop(self):
        self.running = False


class WriteThread(Thread):
    def __init__(self, machine, ser):
        self.machine = machine
        self.ser = ser
        self.queue = machine.queue
        self.num = 0
        super(WriteThread, self).__init__()

    def run(self):
        logging.info("Write thread active")
        self.running = True
        while self.running:
            try:
                data = self.queue.get()
                while self.machine.queueDepth > 5:
                    time.sleep(.1)
                self.machine.queueDepth += 1
                self.ser.write(bytes(data+'\r', encoding='UTF-8'))
                self.queue.task_done()
                logging.warning(" Writing %4d:%s" % (self.machine.queueDepth, data))

                # Pause a bit if writing to the eeprom or resetting
                if data.startswith(('$', chr(24))):
                    time.sleep(2.)

                # Ask for the machine's status periodically
                self.num += 1
                if self.num % POSITION_POLL_FREQ == 0:
                    self._getStatus()
            except Empty:
                self._getStatus()

        logging.info("Write thread exiting")

    def _getStatus(self):
        self.num = 0
        self.ser.write(bytes('?', encoding='utf-8'))

    def stop(self):
        self.running = False
