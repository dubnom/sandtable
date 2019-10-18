import socket
import socketserver
import time
import logging
import queue
from tcpserver import *
from threading import Thread, Event 
import json
from Sand import *

class Machine:
    """ Base class for communicating with a CNC controller.
    
        Subclasses must implement:
            initialize - connect and initialize the actual machine (through serial,
                         API, etc.) it expects:
                             machInitialize - settings like motor mapping, acceleration, etc.
                             This initialization should be sent if not None.
            home - home the machine.
            halt - halt the machine.
            stop - disconnect from the machine.
    """

    pos = [-1., -1.]
    ready = False

    def __init__(self, params, fullInit):
        # FIX: Add machine specific parameters as a dictionary
        self.queue = queue.Queue()
        self.initialize(params, fullInit)

    def send(self, data):
        self.queue.put(data)

    def home(self):
        pass

    def halt(self):
        pass

    def wait(self):
        self.queue.join()

    def flush(self):
        while not self.queue.empty():
            self.queue.get()
            self.queue.task_done()

    def stop(self):
        pass

