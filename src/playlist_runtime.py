from threading import Thread, Lock

from Sand import drawers, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS, MACHINE_UNITS, MACHINE_FEED
from sandable import sandableFactory, SandException
from dialog import Dialog
from history import History
from playlist import Playlist
import mach
import schedapi


class PlaylistRunner:
    IDLE = 'idle'
    PLAYING = 'playing'
    STOPPING = 'stopping'
    ABORTING = 'aborting'
    ERROR = 'error'

    def __init__(self):
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
                'name': Playlist.active_name(),
                'state': self._state,
                'message': self._message,
                'current': current,
                'currentIndex': self._currentIndex,
                'total': self._total,
                'mode': self._mode,
                'count': len(Playlist.list()),
            }

    def start_all(self):
        items = Playlist.list()
        if not items:
            self._set_state(state=self.ERROR, message='Playlist is empty', current=None, currentIndex=0, total=0, mode='all')
            return False, 'Playlist is empty'
        return self._start(items, 'all')

    def start_one(self, itemId):
        items = Playlist.list()
        item = next((entry for entry in items if str(entry.get('id', '')) == str(itemId)), None)
        if not item:
            self._set_state(state=self.ERROR, message='Playlist item was not found', current=None, currentIndex=0, total=0, mode='one')
            return False, 'Playlist item was not found'
        return self._start([item], 'one')

    def _start(self, items, mode):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False, 'Playlist is already running'
            self._stopRequested = False
            self._abortRequested = False
            self._state = self.PLAYING
            self._message = 'Starting playlist'
            self._current = None
            self._currentIndex = 0
            self._total = len(items)
            self._mode = mode
            self._thread = Thread(target=self._run_items, args=(items, mode), daemon=True)
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
            self._stopRequested = True
            self._abortRequested = True
            self._state = self.ABORTING
            self._message = 'Aborting playlist and machine'
        try:
            with schedapi.schedapi() as sched:
                sched.demoHalt()
        except Exception:
            pass
        try:
            with mach.mach() as engine:
                engine.stop()
        except Exception:
            pass
        return True, 'Aborting playlist'

    def _should_stop(self):
        with self._lock:
            return self._stopRequested

    def _should_abort(self):
        with self._lock:
            return self._abortRequested

    def _run_items(self, items, mode):
        try:
            with schedapi.schedapi() as sched:
                sched.demoHalt()
        except Exception:
            pass

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
                ok, message = _run_playlist_item(item, wait=True)
                if not ok:
                    self._set_state(state=self.ERROR, message=message, current=item, currentIndex=index, total=len(items), mode=mode)
                    return
                if self._should_abort():
                    self._set_state(state=self.IDLE, message='Playlist aborted', current=None, currentIndex=0, total=len(items), mode=mode)
                    return

            if self._should_abort():
                self._set_state(state=self.IDLE, message='Playlist aborted', current=None, currentIndex=0, total=len(items), mode=mode)
            elif self._should_stop():
                self._set_state(state=self.IDLE, message='Playlist stopped', current=None, currentIndex=0, total=len(items), mode=mode)
            else:
                self._set_state(state=self.IDLE, message='Playlist complete', current=None, currentIndex=0, total=len(items), mode=mode)
        finally:
            with self._lock:
                self._thread = None
                self._stopRequested = False
                self._abortRequested = False
                if self._state not in (self.ERROR,):
                    self._current = None
                    self._currentIndex = 0


def _run_playlist_item(item, wait=False):
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
    except SandException as e:
        return False, str(e)

    boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
    History.history(params, method, chains)
    with mach.mach() as engine:
        engine.run(chains, boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS, wait='True' if wait else False)

    return True, 'Started %s' % method


runner = PlaylistRunner()
