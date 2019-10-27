import logging
from threading import Thread
from machine import Machine


class machiner(Machine):
    """ CNC Machine that doesn't do anything other than log requests.
        This is useful for debugging, or if you don't have a CNC machine
        handy and want to generate patterns anyway."""

    def initialize(self, params, fullInit):
        self.writeThread = NoWriteThread(self)
        self.writeThread.start()
        self.ready = True

    def stop(self):
        self.writeThread.stop()


class NoWriteThread(Thread):
    def __init__(self, machine):
        self.queue = machine.queue
        super(NoWriteThread, self).__init__()

    def run(self):
        logging.info("Write thread active")
        self.running = True
        while self.running:
            data = self.queue.get()
            logging.info("Writing %s" % data.strip())
            self.queue.task_done()
        logging.info("Write thread exiting")

    def stop(self):
        self.running = False
