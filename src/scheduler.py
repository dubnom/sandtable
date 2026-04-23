#!/usr/bin/python3 -u
from pytz import utc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
import json
import socket
import socketserver
from tcpserver import StoppableTCPServer
from threading import Thread
from collections import deque
import random

from Sand import DATA_PATH, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS,\
   MACHINE_UNITS, MACHINE_ACCEL, MACHINE_FEED,\
   SCHEDULER_ENABLE, SCHEDULER_HOST, SCHEDULER_PORT, drawers,\
   LED_COLUMNS, LED_ROWS
from sandable import sandableFactory
from dialog import Params
from Chains import Chains
from history import History
import mach
from ledable import ledPatternFactory
import ledapi

# Parameters
POLLING_DELAY = 0.100     # 1/10 second
DRAW_TIME_MIN = 18        # 18 Seconds
DRAW_TIME_MAX = 25*60     # 25 minutes
PROX_SWITCH_SECS = 8         # Number of seconds to wait for taps


# Advanced job scheduler setup

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///%sjobs.sqlite' % DATA_PATH)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 3
}

#
# Job actions:
#   "demo"   Run a single demo
#   "method" Draw a specific method
#   "saved"  Draw a saved drawing
#
# Job frequency:
#   "yearly" Run at a specific time and date of the year
#       Data is Hour, Minute, Month, Day
#   "daily" Run at a specific time of the day
#       Data is Hour, Minute
#   "frequency" Run at a specific frequency recurring forever
#       Data is Type (DayOfWeek,Month,Day,Year), Value, Hour, Minute


def JobDemo():
    demo.demoOnce()


class Demo(Thread):
    DIE, QUIET, HALT, RUNNING = -1, 0, 1, 2

    def __init__(self, pause=30):
        super(Demo, self).__init__()
        self._state = self.QUIET
        self._count = 0
        self._pause = pause

    def run(self):
        logging.info("Demo active")
        while self._state != self.DIE:
            if self._state == self.QUIET:
                time.sleep(POLLING_DELAY)

            elif self._state == self.RUNNING:
                self._lightsRandom()
                while self._state == self.RUNNING and self._count != 0:
                    self._count -= 1
                    self._drawRandom()
                    self._drawWait()
                    end = time.time() + self._pause
                    while self._state == self.RUNNING and time.time() < end:
                        time.sleep(POLLING_DELAY)
                self._lightsOff()
                if self._state == self.RUNNING:
                    self._state = self.QUIET

            if self._state == self.HALT:
                self._lightsOff()
                self._drawHalt()
                self._state = self.QUIET
        logging.info("Demo exiting")

    def demoContinuous(self, count=-1):
        logging.info("demoContinuous(%d) has been called" % count)
        self._count = count
        self._state = self.RUNNING

    def demoOnce(self):
        self.demoContinuous(1)

    def demoHalt(self):
        logging.info("demoHalt has been called")
        if self._state == self.RUNNING:
            self._state = self.HALT

    def stop(self):
        self._state = self.DIE

    def _lightsRandom(self):
        pattern = ledPatternFactory('RandomLights', LED_COLUMNS, LED_ROWS)
        params = Params(pattern.editor)
        params['minutes'] = 2.0
        with ledapi.ledapi() as led:
            led.setPattern('RandomLights', params)

    def _lightsOff(self):
        pattern = ledPatternFactory('Off', LED_COLUMNS, LED_ROWS)
        params = Params(pattern.editor)
        with ledapi.ledapi() as led:
            led.setPattern('Off', params)

    def _drawRandom(self):
        boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
        while True:
            if self._state == self.HALT:
                return
            drawer = drawers[random.randint(0, len(drawers)-1)]
            sand = sandableFactory(drawer, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
            params = Params(sand.editor)
            params.randomize(sand.editor)
            try:
                chains = sand.generate(params)
                pchains = Chains.convertUnits(chains, TABLE_UNITS, MACHINE_UNITS)
                pchains = Chains.bound(chains, boundingBox)
                t, d, p = Chains.estimateMachiningTime(pchains, MACHINE_FEED, MACHINE_ACCEL)
                if DRAW_TIME_MIN <= t <= DRAW_TIME_MAX:
                    break
                logging.info("Tried %s but time was %d:%02d" % (sand, int(t/60), int(t) % 60))
            except Exception as e:
                logging.warning("Tried %s but failed with %s" % (sand, e))

        logging.info("Drawing %s, estimated time %d:%02d" % (sand, int(t/60), int(t) % 60))
        History.save(params, drawer, chains, "lastdemo")
        with mach.mach() as e:
            e.run(chains, boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS)

    def _drawWait(self):
        with mach.mach() as e:
            while self._state == self.RUNNING and not e.getStatus()['ready']:
                time.sleep(POLLING_DELAY)

    def _drawHalt(self):
        with mach.mach() as e:
            e.stop()

class MyHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super(MyHandler, self).setup()
        self.demo = self.server.demo

    def handle(self):
        req = self.rfile.readline().strip()
        command, data = json.loads(req)
        logging.debug("Command: %s, %s" % (command, data))
        if command == 'status':
            pass
        elif command == 'demoOnce':
            self.demo.demoOnce()
        elif command == 'demoContinuous':
            self.demo.demoContinuous()
        elif command == 'demoHalt':
            self.demo.demoHalt()
        elif command == 'restart':
            self._restart()
        elif command == 'jobAdd':
            self._jobAdd(data)
        elif command == 'jobDelete':
            pass    # FIX: Finish code
        elif command == 'jobList':
            pass    # FIX: Finish code
        else:
            logging.warning("Unknown command: %s" % command)
        self.wfile.write(bytes(json.dumps({'state': self.demo._state})+'\n', encoding='utf-8'))

    def _restart(self):
        self.server.stop()

    def _jobAdd(data):
        pass    # FIX: CODE ISN'T DONE


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Starting the SandTable scheduler daemon')

    demo = Demo()
    demo.start()

    # Start the background job scheduler (which potentially means start servicing jobs)
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
    scheduler.start()

    # FIX: Kluge to clear out the scheduler and start a random drawing everyday at 3:00 am.
    def kluge():
        logging.info("Kluge triggered")
        if SCHEDULER_ENABLE:
            logging.info("Running single demo")
            demo.demoOnce()
        else:
            logging.info("Schedule is disabled")
        logging.info("Kluge returned")

    for job in scheduler.get_jobs():
        job.remove()
    job = scheduler.add_job(kluge, 'cron', hour=7)

    # Start the socket server and listen for requests
    # Retry logic has been implemented because sometimes sockets don't release quickly
    logging.info("Trying to listen on %s:%d" % (SCHEDULER_HOST, SCHEDULER_PORT))
    retries = 10
    server = None
    while retries > 0:
        try:
            server = StoppableTCPServer((SCHEDULER_HOST, SCHEDULER_PORT), MyHandler)
            logging.info("SocketServer connected")
            break
        except socket.error as e:
            logging.error("%d retries left: %s" % (retries, e))
            retries -= 1
            time.sleep(10.0)
    if server:
        server.demo = demo
        server.serve()
    logging.info("Out of server loop!")

    scheduler.shutdown()
    demo.stop()

    exit(1)
