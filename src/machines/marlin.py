import serial
import logging
from threading import Thread
from queue import Empty
import time
import re
from machine import Machine


POSITION_POLL_FREQ = 30     # Poll for status every 30 instructions
POSITION_POLL_TIME = 5      # Or every 5 seconds

class machiner(Machine):
    """ Driver for Marlin compatible controllers."""

    started = False

    def initialize(self, params, fullInit):
        logging.info('Trying to connect to Marlin controller.')

        # Open the serial port to connect to Marlin
        try:
            self.ser = serial.Serial(params['port'], baudrate=params['baud'], rtscts=False, timeout=0.5)
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
        fullInit = True     # FIX: Board doesn't seem to remember anything
        if fullInit:
            logging.info('Full machine initialization.')
            initialize += params['init'] + ['M500', 'G1 Z1', 'M114']

        for i in initialize:
            self.send(i)

        # Home the machine
        self.home()
        self.ready = True

    def run(self, chains, units, feed):
        self.ready = False
        self.send('M17')
        self.send('G1 F%g' % feed)
        self.send('G1 Z0')
        count = 0
        for chain in chains:
            for point in chain:
                s = 'G1 X%g Y%g' % (round(point[0], 1), round(point[1], 1))
                self.send(s)
                count += 1
                if count % POSITION_POLL_FREQ == 0:
                    self.send('M114')
        self.send('G1 Z1')
        self.send('M18')
        self.send("M114")

    def home(self):
        self.send('G28.2X0Y0')

    def halt(self):
        self.flush()
        self.send('G1 Z1')
        self.send("M18")
        self.send("M114")

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
        logging.info("Read thread active")
        reStatus = re.compile(r'^X:([\d.-]+) Y:([\d.-]+) Z:([\d.-]+) .+$')
        self.running = True
        while self.running:
            line = self.ser.readline().decode(encoding='utf-8').strip()
            if len(line):
                logging.debug("<"+line)
                if line.startswith('Marlin'):
                    self.machine.started = True
                elif line.startswith('ok'):
                    self.machine.queueDepth -=1
                    logging.warning( "ok: %4d" % self.machine.queueDepth )

                elif line.startswith('error'):
                    self.machine.queueDepth -= 1
                    logging.error( "error: %04d %s" % line )

                else:
                    try:
                        match = reStatus.match(line)
                        if match:
                            self.machine.pos[0] = float(match.groups()[0])
                            self.machine.pos[1] = float(match.groups()[1])
                            # Use the Z axis as a way of determining that a drawing has ended (0-busy, 1-ready)
                            self.machine.ready = 'Busy' if float(match.groups()[2]) > .5 else 'Idle'

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
        while not self.machine.started:
            time.sleep(.1)
        while self.running:
            try:
                data = self.queue.get(timeout=POSITION_POLL_TIME)
                while self.machine.queueDepth > 7:
                    time.sleep(.1)
                self.machine.queueDepth += 1
                self.ser.write(bytes(data+'\r', encoding='UTF-8'))
                self.queue.task_done()
                logging.warning(" Writing %4d:%s" % (self.machine.queueDepth, data))

                # Pause a bit if writing to the eeprom or resetting
                if data.startswith(('$', chr(24))):
                    time.sleep(2.)

                # Ask for the machine's status periodically
                #self.num += 1
                #if self.num % POSITION_POLL_FREQ == 0:
                #    self._getStatus()
            except Empty:
                #self._getStatus()
                pass
        logging.info("Write thread exiting")

    def _getStatus(self):
        self.num = 0
        self.ser.write(bytes('M114\r', encoding='utf-8'))

    def stop(self):
        self.running = False
