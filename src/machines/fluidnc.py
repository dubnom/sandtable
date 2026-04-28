import serial
from threading import Thread
import logging
from queue import Empty
import re
import time
from machine import Machine


POLL_TIME = 5      #  Time to wait for queue
MAX_QUEUE_DEPTH = 10

HOMING_SEQUENCE = [
    '$X',       # Reset   
    '$10=2',    # Report work coordinates
    '$11=1',    # Junction deviation mm
    '$Report/Interval=2000', # Reporting period
    '$H',       # Home
    'G54',      # G54 work offset
    'G90',      # Absolute mode
]


class machiner(Machine):
    """Driver for FLUIDNC compatible controllers."""

    def initialize(self, params, fullInit):
        logging.info('Trying to connect to FLUIDNC controller.')

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

        logging.info('Waiting for controller to be ready')
        while not self.reader.ready:
            time.sleep(.2)
        logging.info('Grbl ready')
            
        self.send_many(initialize)

    def send_many(self, cmds):
        for cmd in cmds:
            self.send(cmd)

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
        self.send_many(HOMING_SEQUENCE)

    def halt(self):
        self.flush()
        self.writer._write_raw(b'\r\x18')

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
        reStatus = re.compile(r'^<(Idle|Run|Alarm)\|WPos:([\d.-]+),([\d.-]+),([\d.-]+)\|(.*)>$')

        logging.info("Read thread active")
        self.running = True
        while self.running:
            line = self.ser.readline()
            if line and len(line):
                line = line.decode(encoding='utf-8').strip()
                logging.debug(line)

                # Parse the lines for status here
                if line.startswith('Grbl'):
                    self.ready = True
                else:
                    try:
                        # Parse status reports
                        match = reStatus.match(line)
                        if match:
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
        # Write a reset command to get things started
        self._write_raw(b'\r\x18')

        while self.running:
            try:
                data = self.queue.get(timeout=POLL_TIME)
                while self.machine.queueDepth > MAX_QUEUE_DEPTH:
                    time.sleep(.1)
                self.machine.queueDepth += 1
                self._write(data)
                self.queue.task_done()
                logging.warning(" Writing %4d:%s" % (self.machine.queueDepth, data))

            except Empty:
                pass

        logging.info("Write thread exiting")

    def _write(self, data):
        self._write_raw(bytes(data+'\r', encoding='UTF-8'))

    def _write_raw(self, data):
        self.ser.write(data)

    def stop(self):
        self.running = False
