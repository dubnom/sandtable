import serial
from threading import Thread
import logging
from queue import Empty
import re
from machine import Machine


POSITION_POLL_FREQ = 30     # Poll for status every 30 instructions
POSITION_POLL_SECS = 2.     # Or every 2. seconds


class machiner(Machine):
    """ Driver for SmoothieWare compatible controllers."""

    def initialize(self, params, fullInit):
        logging.info('Trying to connect to Smoothie controller.')

        # Open the serial port to connect to Smoothie
        try:
            self.ser = serial.Serial(params['port'], baudrate=params['baud'], rtscts=True, timeout=0.5)
        except Exception as e:
            logging.error(e)
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
            initialize += params['init']

        for i in initialize:
            self.send(i)

        # Home the machine
        self.home()

    def run(self, chains, units, feed):
        self.send('G20' if units == 'inches' else 'G21')
        self.send('F%g' % feed)
        self.count = 0
        for chain in chains:
            for point in chain:
                s = 'G1 X%g Y%g' % (round(point[0], 2), round(point[1], 2))
                self.send(s)
                self.count += 1
        self.send('M2')

    def home(self):
        self.send('G28.2X0Y0')

    def halt(self):
        self.flush()
        self.send("abort")

    def stop(self):
        self.writer.stop()
        self.reader.stop()
        self.ser.close()


class ReadThread(Thread):
    def __init__(self, machine, ser):
        self.ser = ser
        super(ReadThread, self).__init__()

    def run(self):
        reStatus = re.compile(r'^<(Idle|Run)\\|MPos:([\d.-]+),([\d.-]+),([\d.-]+)\\|(.*)>$')

        logging.info("Read thread active")
        self.running = True
        while self.running:
            line = self.ser.readline().decode(encoding='utf-8').strip()
            if len(line):
                # Parse the lines for status here
                try:
                    # Parse status reports
                    match = reStatus.match(line)
                    if match:
                        status = match.groups()[0]
                        self.machine.pos[0], self.machine.pos[1] = float(match.groups()[1]), float(match.groups()[2])
                        self.machine.ready = status == 'Idle'

                    # Parse responses
                    elif line == 'ok':
                        pass

                    # Everything else
                    else:
                        logging.warning("Received: %s" % line)
                except ValueError:
                    logging.warning("Couldn't parse: %s" % line)
        logging.info("Read thread exiting")

    def stop(self):
        self.running = False


class WriteThread(Thread):
    def __init__(self, machine, ser):
        self.ser = ser
        self.queue = machine.queue
        self.num = 0
        super(WriteThread, self).__init__()

    def run(self):
        logging.info("Write thread active")
        self.running = True
        while self.running:
            try:
                data = self.queue.get(True, POSITION_POLL_SECS)
                self.ser.write(bytes(data+'\r', encoding='UTF-8'))
                self.queue.task_done()

                # Ask for the machine's status periodically
                self.num += 1
                if self.num % POSITION_POLL_FREQ == 0:
                    self._getStatus()
            except Empty:
                self._getStatus()

        logging.info("Write thread exiting")

    def _getStatus(self):
        self.num = 0
        self.ser.write(bytes('get status\r', encoding='utf-8'))

    def stop(self):
        self.running = False
