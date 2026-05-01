#!/usr/bin/python3 -u
import logging
import socket
import json
import time
import socketserver
from threading import Thread, Lock
from importlib import import_module
from tcpserver import StoppableTCPServer
from Chains import Chains
from Sand import MACH_HOST, MACH_PORT, STATUS_HOST, STATUS_PORT, MACHINE, VER_FILE, MACHINE_PARAMS, drawers, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS, MACHINE_UNITS, MACHINE_FEED, MACHINE_ACCEL
from sandable import sandableFactory, SandException
from dialog import Dialog
from history import History


class DrawingStatus:
    IDLE = 'idle'
    RUNNING = 'running'

    def __init__(self):
        self._lock = Lock()
        self._reset_locked()

    def _reset_locked(self):
        self._active = False
        self._title = ''
        self._method = ''
        self._source = ''
        self._message = 'Idle'
        self._startedAt = 0.0
        self._estimatedSeconds = 0.0
        self._distance = 0.0
        self._pointCount = 0
        self._units = MACHINE_UNITS
        self._seenBusy = False

    def clear(self, message='Idle'):
        with self._lock:
            self._reset_locked()
            self._message = message

    def start(self, chains, feed, meta=None):
        meta = dict(meta) if isinstance(meta, dict) else {}
        try:
            estimatedSeconds, distance, pointCount = Chains.estimateMachiningTime(chains, feed, MACHINE_ACCEL)
        except Exception:
            estimatedSeconds, distance, pointCount = 0.0, 0.0, 0

        title = str(meta.get('title') or meta.get('method') or 'Drawing')
        method = str(meta.get('method') or '')
        source = str(meta.get('source') or 'draw')

        with self._lock:
            self._active = True
            self._title = title
            self._method = method
            self._source = source
            self._message = 'Drawing %s' % title
            self._startedAt = time.time()
            self._estimatedSeconds = float(estimatedSeconds)
            self._distance = float(distance)
            self._pointCount = int(pointCount)
            self._units = MACHINE_UNITS
            self._seenBusy = False

    def snapshot(self, machineStatus):
        with self._lock:
            if not self._active:
                return {
                    'state': self.IDLE,
                    'message': self._message,
                    'title': '',
                    'method': '',
                    'source': '',
                    'elapsedSeconds': 0,
                    'estimatedSeconds': 0,
                    'remainingSeconds': 0,
                    'percentComplete': None,
                    'pointCount': 0,
                    'distance': 0.0,
                    'distanceUnits': self._units,
                }

            ready = bool(machineStatus.get('ready'))
            elapsedSeconds = max(0.0, time.time() - self._startedAt)
            if not self._seenBusy and not ready:
                self._seenBusy = True

            finished = False
            if self._seenBusy and ready and elapsedSeconds >= 0.5:
                finished = True
            elif (not self._seenBusy) and ready and self._estimatedSeconds > 0 and elapsedSeconds >= self._estimatedSeconds:
                finished = True

            if finished:
                self._reset_locked()
                self._message = 'Idle'
                return {
                    'state': self.IDLE,
                    'message': self._message,
                    'title': '',
                    'method': '',
                    'source': '',
                    'elapsedSeconds': 0,
                    'estimatedSeconds': 0,
                    'remainingSeconds': 0,
                    'percentComplete': None,
                    'pointCount': 0,
                    'distance': 0.0,
                    'distanceUnits': self._units,
                }

            remainingSeconds = max(0.0, self._estimatedSeconds - elapsedSeconds)
            percentComplete = None
            if self._estimatedSeconds > 0:
                percentComplete = min(99.0, (elapsedSeconds / self._estimatedSeconds) * 100.0)

            return {
                'state': self.RUNNING,
                'message': self._message,
                'title': self._title,
                'method': self._method,
                'source': self._source,
                'elapsedSeconds': int(elapsedSeconds),
                'estimatedSeconds': int(self._estimatedSeconds),
                'remainingSeconds': int(remainingSeconds),
                'percentComplete': round(percentComplete, 1) if percentComplete is not None else None,
                'pointCount': self._pointCount,
                'distance': self._distance,
                'distanceUnits': self._units,
            }


class ServerStatusPublisher(Thread):
    def __init__(self, snapshot_provider):
        super(ServerStatusPublisher, self).__init__(daemon=True)
        self._snapshot_provider = snapshot_provider
        self._running = True
        self._host = STATUS_HOST
        self._port = STATUS_PORT

    def publish(self, payload=None):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self._host, self._port))
                message = json.dumps(payload if payload is not None else self._snapshot_provider()) + '\n'
                sock.sendall(message.encode('utf-8'))
        except Exception as error:
            logging.debug('Unable to publish machd status update: %s', error)

    def run(self):
        while self._running:
            self.publish()
            time.sleep(2.0)

    def stop(self):
        self._running = False


class PlaylistRunner:
    IDLE = 'idle'
    PLAYING = 'playing'
    STOPPING = 'stopping'
    ABORTING = 'aborting'
    ERROR = 'error'

    def __init__(self, machine, drawing):
        self.machine = machine
        self.drawing = drawing
        self._lock = Lock()
        self._thread = None
        self._reset_locked()

    def _reset_locked(self):
        self._state = self.IDLE
        self._message = ''
        self._current = None
        self._currentIndex = 0
        self._total = 0
        self._stopRequested = False
        self._abortRequested = False
        self._mode = 'all'

    def _set_state(self, state=None, message=None, current=None, currentIndex=None, total=None, mode=None):
        with self._lock:
            if state is not None:
                self._state = state
            if message is not None:
                self._message = message
            if current is not None or current is None:
                self._current = current
            if currentIndex is not None:
                self._currentIndex = currentIndex
            if total is not None:
                self._total = total
            if mode is not None:
                self._mode = mode

    def status(self):
        with self._lock:
            current = dict(self._current) if isinstance(self._current, dict) else None
            return {
                'state': self._state,
                'message': self._message,
                'current': current,
                'currentIndex': self._currentIndex,
                'total': self._total,
                'mode': self._mode,
            }

    def start(self, items, mode='all'):
        playlistItems = [dict(item) for item in items if isinstance(item, dict)]
        if not playlistItems:
            self._set_state(state=self.ERROR, message='Playlist is empty', current=None, currentIndex=0, total=0, mode=mode)
            return False, 'Playlist is empty'

        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False, 'Playlist is already running'
            self._stopRequested = False
            self._abortRequested = False
            self._state = self.PLAYING
            self._message = 'Starting playlist'
            self._current = None
            self._currentIndex = 0
            self._total = len(playlistItems)
            self._mode = mode
            self._thread = Thread(target=self._run_items, args=(playlistItems, mode), daemon=True)
            self._thread.start()
        return True, 'Playlist started'

    def stop(self):
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._state = self.IDLE
                self._message = 'Playlist is idle'
                return False, 'Playlist is idle'
            self._stopRequested = True
            self._state = self.STOPPING
            self._message = 'Stopping after current drawing'
        return True, 'Stopping playlist'

    def abort(self):
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._state = self.IDLE
                self._message = 'Playlist is idle'
                return False, 'Playlist is idle'
            self._stopRequested = True
            self._abortRequested = True
            self._state = self.ABORTING
            self._message = 'Aborting playlist and machine'
        try:
            self.machine.halt()
            self.drawing.clear('Playlist aborted')
        except Exception as error:
            logging.warning('Unable to halt machine during playlist abort: %s', error)
        return True, 'Aborting playlist'

    def _schedule_message_clear(self, delay=5):
        def _clear():
            time.sleep(delay)
            with self._lock:
                self._message = ''
        Thread(target=_clear, daemon=True).start()

    def _should_stop(self):
        with self._lock:
            return self._stopRequested

    def _should_abort(self):
        with self._lock:
            return self._abortRequested

    def _wait_for_machine(self):
        time.sleep(0.5)
        self.machine.wait()
        while not self.machine.getStatus().get('ready', False):
            if self._should_abort():
                return False
            time.sleep(0.5)
        return True

    def _run_item(self, item):
        method = str(item.get('method', ''))
        if method not in drawers:
            return False, 'Invalid method "%s"' % method

        rawParams = item.get('params', {})
        if not isinstance(rawParams, dict):
            rawParams = {}

        sand = sandableFactory(method, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
        dialog = Dialog(sand.editor, rawParams, None)
        params = dialog.getParams()

        try:
            chains = sand.generate(params)
        except SandException as error:
            return False, str(error)

        History.history(params, method, chains)
        boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
        machChains = Chains.bound(chains, boundingBox)
        machChains = Chains.convertUnits(machChains, TABLE_UNITS, MACHINE_UNITS)
        machChains = Chains.round(machChains, 2)
        self.drawing.start(machChains, MACHINE_FEED, {
            'title': item.get('title') or method,
            'method': method,
            'source': 'playlist',
        })
        self.machine.flush()
        self.machine.run(machChains, MACHINE_UNITS, MACHINE_FEED)
        if not self._wait_for_machine():
            self.drawing.clear('Playlist aborted')
            return False, 'Playlist aborted'
        return True, 'Started %s' % method

    def _run_items(self, items, mode):
        try:
            for index, item in enumerate(items, start=1):
                if self._should_stop():
                    break
                self._set_state(
                    state=self.PLAYING,
                    message='Drawing %s' % item.get('title', item.get('method', 'Playlist item')),
                    current=item,
                    currentIndex=index,
                    total=len(items),
                    mode=mode,
                )
                ok, message = self._run_item(item)
                if not ok:
                    if self._should_abort():
                        self._set_state(state=self.IDLE, message='Playlist aborted', current=None, currentIndex=0, total=len(items), mode=mode)
                    else:
                        self._set_state(state=self.ERROR, message=message, current=item, currentIndex=index, total=len(items), mode=mode)
                    self._schedule_message_clear()
                    return

            if self._should_abort():
                self._set_state(state=self.IDLE, message='Playlist aborted', current=None, currentIndex=0, total=len(items), mode=mode)
            elif self._should_stop():
                self._set_state(state=self.IDLE, message='Playlist stopped', current=None, currentIndex=0, total=len(items), mode=mode)
            else:
                self._set_state(state=self.IDLE, message='Playlist complete', current=None, currentIndex=0, total=len(items), mode=mode)
            self._schedule_message_clear()
        finally:
            with self._lock:
                self._thread = None
                self._stopRequested = False
                self._abortRequested = False
                if self._state != self.ERROR:
                    self._current = None
                    self._currentIndex = 0


class MyHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super(MyHandler, self).setup()
        self.machine = self.server.machine
        self.playlist = self.server.playlist
        self.drawing = self.server.drawing
        self.publisher = self.server.publisher

    def handle(self):
        req = self.rfile.readline().strip()
        try:
            command, data = json.loads(req)
        except json.decoder.JSONDecodeError as e:
            logging.info(e)
            return

        commandResult = {'ok': True, 'message': ''}
        if command != 'status':
            logging.info("Command: %s" % command)
        if command == 'send':
            self.machine.send(data['string'])
        elif command == 'run':
            self.run(data)
        elif command == 'playlistStart':
            commandResult = self.playlistStart(data)
        elif command == 'playlistStop':
            commandResult = self.playlistStop()
        elif command == 'playlistAbort':
            commandResult = self.playlistAbort()
        elif command == 'playlistStatus':
            pass
        elif command == 'halt':
            self.machine.halt()
            self.drawing.clear('Halted')
        elif command == 'home':
            self.machine.home()
            self.drawing.clear('Idle')
        elif command == 'restart':
            self.restart()

        status = self.server.status_snapshot()
        status['result'] = commandResult
        self.publisher.publish(status)
        self.wfile.write(bytes(json.dumps(status)+'\n', 'utf-8'))

    def run(self, data):
        chains = data['chains']
        units = data['units']
        feed = data['feed']
        wait = data['wait']
        meta = data.get('meta', {})

        self.machine.flush()
        self.drawing.start(chains, feed, meta)
        self.machine.run(chains, units, feed)

        if wait in (True, 'True', 'true'):
            logging.info("Waiting for drawing to finish")
            self.machine.wait()
            logging.debug("Queue depth is fine, waiting for machine to become ready")
            while not self.machine.getStatus().get('ready', False):
                time.sleep(0.5)
            logging.debug("Status has changed")
        logging.info("Run has completed")

    def playlistStart(self, data):
        items = data.get('items', [])
        mode = data.get('mode', 'all')
        ok, message = self.playlist.start(items, mode)
        if not ok:
            logging.warning(message)
        return {'ok': ok, 'message': message}

    def playlistStop(self):
        ok, message = self.playlist.stop()
        if not ok:
            logging.warning(message)
        return {'ok': ok, 'message': message}

    def playlistAbort(self):
        ok, message = self.playlist.abort()
        if not ok:
            logging.warning(message)
        return {'ok': ok, 'message': message}

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
        server.drawing = DrawingStatus()
        server.playlist = PlaylistRunner(machine, server.drawing)
        server.status_snapshot = lambda: _status_snapshot(server.machine, server.playlist, server.drawing)
        server.publisher = ServerStatusPublisher(server.status_snapshot)
        server.publisher.start()
        server.serve()
    logging.info("Out of server loop!")

    if server and getattr(server, 'publisher', None):
        server.publisher.stop()

    # Close everything down
    logging.info("Stopping machine")
    machine.stop()
    logging.info("Should be all done. Shut down.")


def _status_snapshot(machine, playlist, drawing):
    status = machine.getStatus()
    status['playlist'] = playlist.status()
    status['drawing'] = drawing.snapshot(status)
    return status


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
