import serial
from threading import Thread
import json
import time
import logging
from machine import Machine


class machiner(Machine):
    """ Driver for Tinyg compatible controllers."""

    state = 0
    queueDepth = 32

    def initialize(self, params, fullInit):
        logging.info('Trying to connect to Tinyg controller.')

        # Open the serial port to connect to Tinyg
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
        initialize = [
            {"rv": ""},                      # Software version
            {"rb": ""},                      # Software build
            {"ex": 2},                       # Use CTS/RTS for flow control
            {"jv": 4},                       # Line numbers
            {"qv": 2},                       # Verbose queue reports
            {"gun": 0},                      # Inches
            {"sv": 1},                       # Status reports (filtered)
        ]
        if fullInit:
            initialize += params['init']
        for i in initialize:
            self.send(json.dumps(i))
        # After making settings we either need to reset (and wait) or just wait a little bit
        if fullInit:
            self.send("\x18")
            time.sleep(6.)
        else:
            time.sleep(.5)

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
        logging.info("Read thread active")
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
                            self.machine.pos[0] = status['posx']
                        if 'posy' in status:
                            self.machine.pos[1] = status['posy']
                        if 'stat' in status:
                            self.machine.state = status['stat']
                            self.machine.ready = self.machine.state in (1, 3, 4)
                            logging.debug("State: %d" % self.machine.state)

                    # Parse queue reports
                    elif 'qr' in data:
                        self.machine.queueDepth = data['qr']
                        logging.debug("QueueDepth: %d" % self.machine.queueDepth)

                    # Parse responses
                    elif 'r' in data:
                        response = data['r']
                        logging.debug("Response: %s" % response)

                    # Everything else
                    else:
                        logging.debug("Received:", data)
                except ValueError:
                    logging.warning("Couldn't parse: %s" % line)
        logging.info("Read thread exiting")

    def stop(self):
        self.running = False


class WriteThread(Thread):
    def __init__(self, machine, ser):
        self.machine = machine
        self.ser = ser
        self.queue = machine.queue
        super(WriteThread, self).__init__()

    def run(self):
        logging.info("Write thread active")
        self.running = True
        while self.running:
            data = self.queue.get()
            while self.machine.queueDepth < 3:
                time.sleep(.1)
            self.ser.write(bytes(data+'\n', encoding='UTF-8'))
            self.queue.task_done()
        logging.info("Write thread exiting")

    def stop(self):
        self.running = False
