#!/usr/bin/python3 -u
import logging
import socket
import json
import time
import socketserver
from importlib import import_module
from tcpserver import StoppableTCPServer
from Sand import MACH_HOST, MACH_PORT, MACHINE, VER_FILE, MACHINE_PARAMS


class MyHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super(MyHandler, self).setup()
        self.machine = self.server.machine

    def handle(self):
        req = self.rfile.readline().strip()
        try:
            command, data = json.loads(req)
        except json.decoder.JSONDecodeError as e:
            logging.info(e)
            return

        if command != 'status':
            logging.info("Command: %s" % command)
        if command == 'send':
            self.machine.send(data['string'])
        elif command == 'run':
            self.run(data)
        elif command == 'halt':
            self.machine.halt()
        elif command == 'home':
            self.machine.home()
        elif command == 'restart':
            self.restart()

        status = self.machine.getStatus()
        self.wfile.write(bytes(json.dumps(status)+'\n', 'utf-8'))

    def run(self, data):
        chains = data['chains']
        units = data['units']
        feed = data['feed']
        wait = data['wait']

        self.machine.flush()
        self.machine.run(chains, units, feed)

        if wait == 'True':
            logging.info("Waiting for drawing to finish")
            time.sleep(1.0)
            self.machine.wait()
            logging.debug("Queue depth is fine, waiting for state %s" % self.ready)
            while not self.ready:
                time.sleep(0.5)
            logging.debug("Status has changed")
        logging.info("Run has completed")

    def restart(self):
        self.server.stop()


def runMachine(machiner, params, fullInitialization):
    logging.info('Starting the sandtable machine daemon')

    # Connect to the machine
    try:
        machine = machiner(params, fullInitialization)
    except Exception as e:
        logging.error(e)
        exit(0)

    # Home the machine so it is in a known state
    machine.home()

    # Start the socket server and listen for requests
    logging.info("Trying to listen on %s:%d" % (MACH_HOST, MACH_PORT))

    retries = 10
    server = None
    while retries > 0:
        try:
            server = StoppableTCPServer((MACH_HOST, MACH_PORT), MyHandler)
            logging.info("SocketServer connected")
            break
        except socket.error as e:
            logging.error("%d retries left: %s" % (retries, e))
            retries -= 1
            time.sleep(10.0)

    # If SocketServer connected, then start listening and dispatching commands to the machine
    if server:
        server.machine = machine
        server.serve()
    logging.info("Out of server loop!")

    # Close everything down
    logging.info("Stopping machine")
    machine.stop()
    logging.info("Should be all done. Shut down.")


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    machine_module = import_module('machines.%s' % MACHINE)
    machiner = machine_module.machiner

    # Check settings update file
    fullInitialization = True
    try:
        with open(VER_FILE, 'r') as f:
            oldVersion = json.load(f)
        if oldVersion == MACHINE_PARAMS:
            fullInitialization = False
    except Exception as e:
        logging.error(e)

    if fullInitialization:
        with open(VER_FILE, 'w') as f:
            json.dump(MACHINE_PARAMS, f)

    runMachine(machiner, MACHINE_PARAMS, fullInitialization)


main()
exit(1)
