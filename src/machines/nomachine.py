import logging
import queue
from threading import Thread, Event 
from machine import Machine


class machiner(Machine):
    """ CNC Machine that doesn't do anything other than log requests.
        This is useful for debugging, or if you don't have a CNC machine
        handy and want to generate patterns anyway."""

    def initialize(self, machInitialize):
        self.writeThread = NoWriteThread(self)
        self.writeThread.start()

    def stop(self):
        self.writeThread.stop()


class NoWriteThread(Thread):
    def __init__(self,machine):
        self.queue = machine.queue
        super(NoWriteThread, self).__init__()

    def run(self):
        self.running = True
        while self.running:
            data = self.queue.get()
            logging.info( "Writing %s" % data.strip())
            self.queue.task_done()

    def stop(self):
        self.running = False
