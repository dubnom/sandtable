import queue


class Machine:
    """ Base class for communicating with a CNC controller.

        Subclasses must implement:
            initialize - connect and initialize the actual machine (through serial,
                         API, etc.) it expects:
                             machInitialize - settings like motor mapping, acceleration, etc.
                             This initialization should be sent if not None.
            run - draw a pattern on the machine.
            home - home the machine.
            halt - halt the machine.
            stop - disconnect from the machine.
    """

    pos = [-1., -1.]
    ready = False
    count = 0

    def __init__(self, params, fullInit):
        self.queue = queue.Queue()
        self.initialize(params, fullInit)

    def _normalize_ready(self):
        ready = self.ready
        if isinstance(ready, bool):
            return ready
        if isinstance(ready, str):
            state = ready.strip().lower()
            if state in ('idle', 'ready', 'true'):
                return True
            if state in ('busy', 'running', 'run', 'false'):
                return False
        return bool(ready)

    def send(self, data):
        self.queue.put(data)

    def run(self, chains, units, feed):
        pass

    def home(self):
        pass

    def halt(self):
        pass

    def wait(self):
        self.queue.join()

    def flush(self):
        try:
            while True:
                self.queue.get_nowait()
                self.queue.task_done()
        except queue.Empty:
            pass

    def stop(self):
        pass

    def getStatus(self):
        count = self.count
        percent = 100 if count == 0 else (count-self.queue.qsize()) / count
        return {'pos': self.pos, 'ready': self._normalize_ready(), 'percent': percent}
