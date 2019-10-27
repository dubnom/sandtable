import socket
import logging
from threading import Thread
from machine import Machine


class machiner(Machine):
    """ Driver for emc compatible machines.

    FIX: THIS PORT IS UNTESTED
    FIX: 'ready' needs to be imlemented"""

    def intialize(self, params, fullInit):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((params['host'], params['port']))
        self.readThread = ReadThread(self, self.socket)
        self.readThread.start()

        self.send('hello EMC 1 1')
        self.send('set echo off')
        self.send('set verbose on')
        self.send('set enable EMCTOO')
        self.send('set mode manual')
        self.send('set estop off')
        self.send('set machine on')
        self.send('set home 0')
        self.send('set home 1')

        self.home()
        self.ready = True

    def stop(self):
        self.send('quit')
        self.writer.stop()
        self.reader.stop()
        self.socket.close()
        del self.socket

    def halt(self):
        self.send('set estop on')
        self.send('set estop off')
        self.send('set machine on')

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


class ReadThread(Thread):
    def __init__(self, machine, socket):
        super(ReadThread, self).__init__()
        self.machine = machine
        self.socket = socket
        self.file = socket.makefile()

    def run(self):
        logging.info("Read thread active")
        self.running = True
        while self.running:
            line = self.file.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith('JOINT_POS'):
                positions = [float(p) for p in line.split(' ')[1::]]
                self.machine.pos = [positions[0], positions[1]]
        logging.info("Read thread exiting")

    def stop(self):
        self.running = False


class WriteThread(Thread):
    def __init__(self, machine, socket):
        self.socket = socket
        self.queue = machine.queue
        super(WriteThread, self).__init__()

    def run(self):
        logging.info("Write thread active")
        self.running = True
        while self.running:
            # FIX: Add conditional for controller readiness
            data = self.queue.get()
            self.socket.send(bytes(data+'\n', encoding='UTF-8'))
            self.queue.task_done()
        logging.info("Write thread exiting")

    def stop(self):
        self.running = False
