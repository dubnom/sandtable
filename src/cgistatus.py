from flask import jsonify, request
import json
import logging
import socketserver
from threading import Thread

from webapp import app, socketio
from playlist import Playlist
import mach
from tcpserver import StoppableTCPServer
from Sand import STATUS_HOST, STATUS_PORT


def _default_status_payload(message='Machine status unavailable'):
    return {
        'machine': {
            'state': 'unknown',
            'ready': None,
            'message': message,
            'raw': {},
        },
        'playlist': {
            'name': Playlist.active_name(),
            'state': 'idle',
            'message': 'Idle',
            'current': None,
            'currentIndex': 0,
            'total': 0,
            'mode': 'all',
            'count': len(Playlist.list()),
        },
        'drawing': {
            'state': 'idle',
            'message': 'Idle',
            'title': '',
            'method': '',
            'source': '',
            'elapsedSeconds': 0,
            'estimatedSeconds': 0,
            'remainingSeconds': 0,
            'percentComplete': None,
            'pointCount': 0,
            'distance': 0.0,
            'distanceUnits': '',
        },
    }


_lastStatusSnapshot = _default_status_payload()
_statusListener = None


def _emit_admin_update(room=None):
    import cgiadmin

    payload = {'stuff': cgiadmin._status_rows()}
    if room is not None:
        socketio.emit('admin:update', payload, room=room)
        return payload
    socketio.emit('admin:update', payload)
    return payload


def _playlist_status_from_daemon(status=None):
    if status is None:
        return dict(_lastStatusSnapshot.get('playlist', {}))
    playlist = status.get('playlist', {}) if isinstance(status, dict) else {}
    if not isinstance(playlist, dict):
        playlist = {
            'state': 'error',
            'message': 'Playlist status unavailable',
            'current': None,
            'currentIndex': 0,
            'total': 0,
            'mode': 'all',
        }

    payload = dict(playlist)
    payload['name'] = Playlist.active_name()
    payload['count'] = len(Playlist.list())
    return payload


def _drawing_status_from_daemon(status=None):
    if status is None:
        return dict(_lastStatusSnapshot.get('drawing', {}))
    drawing = status.get('drawing', {}) if isinstance(status, dict) else {}
    if not isinstance(drawing, dict):
        drawing = {
            'state': 'error',
            'message': 'Drawing status unavailable',
            'title': '',
            'method': '',
            'source': '',
            'elapsedSeconds': 0,
            'estimatedSeconds': 0,
            'remainingSeconds': 0,
            'percentComplete': None,
            'pointCount': 0,
            'distance': 0.0,
            'distanceUnits': '',
        }
    return drawing


def _playlist_control(action):
    if action == 'play' and not Playlist.list():
        return False, 'Playlist is empty', _playlist_status_from_daemon()

    try:
        with mach.mach() as engine:
            if action == 'play':
                engine.run_playlist(Playlist.list(), 'all')
            elif action == 'stop':
                engine.stop_playlist()
            elif action == 'abort':
                engine.abort_playlist()
            else:
                return False, 'Unknown control action', _playlist_status_from_daemon()
            status = engine.status or {}
    except Exception as error:
        return False, str(error), _playlist_status_from_daemon()

    record_daemon_status(status, force=True)
    result = status.get('result', {}) if isinstance(status, dict) else {}
    playlist = status.get('playlist', {}) if isinstance(status, dict) else {}
    if not isinstance(playlist, dict):
        playlist = _playlist_status_from_daemon()
    else:
        playlist = dict(playlist)
        playlist['name'] = Playlist.active_name()
        playlist['count'] = len(Playlist.list())
    return result.get('ok', False), result.get('message', ''), playlist


def _payload_from_daemon_status(status):
    ready = bool(status.get('ready')) if 'ready' in status else None
    return {
        'machine': {
            'state': 'ready' if ready else 'busy',
            'ready': ready,
            'message': 'Ready' if ready else 'Busy',
            'raw': status,
        },
        'playlist': _playlist_status_from_daemon(status),
        'drawing': _drawing_status_from_daemon(status),
    }


def _status_payload():
    return _lastStatusSnapshot


def record_daemon_status(status, force=False):
    global _lastStatusSnapshot
    if not isinstance(status, dict):
        return _lastStatusSnapshot
    payload = _payload_from_daemon_status(status)
    if force or payload != _lastStatusSnapshot:
        _lastStatusSnapshot = payload
        socketio.emit('statusbar:update', payload)
        _emit_admin_update()
    return payload


class _StatusPushHandler(socketserver.StreamRequestHandler):
    def handle(self):
        req = self.rfile.readline().strip()
        if not req:
            return
        try:
            payload = json.loads(req)
        except json.decoder.JSONDecodeError as error:
            logging.debug('Invalid pushed daemon status payload: %s', error)
            return

        previousReady = bool(_lastStatusSnapshot.get('machine', {}).get('ready'))
        current = record_daemon_status(payload)
        if not previousReady and current.get('machine', {}).get('ready'):
            socketio.emit('draw:complete', {'status': 'done'})


def _start_status_listener():
    global _statusListener
    if _statusListener is not None:
        return
    _statusListener = True

    def _run_server():
        global _statusListener
        retries = 10
        while retries > 0:
            try:
                server = StoppableTCPServer((STATUS_HOST, STATUS_PORT), _StatusPushHandler)
                _statusListener = server
                server.serve()
                return
            except OSError as error:
                logging.error('Status listener bind failed: %s', error)
                retries -= 1
                if retries <= 0:
                    _statusListener = None
                    return
                socketio.sleep(1.0)

    listener = Thread(target=_run_server, daemon=True)
    listener.start()


def _emit_statusbar_update(force=False, room=None):
    payload = _status_payload()
    if room is not None:
        socketio.emit('statusbar:update', payload, room=room)
        return payload
    if force:
        socketio.emit('statusbar:update', payload)
        _emit_admin_update()
    return payload


def signal_draw_started():
    """Backwards-compatible hook for callers that start a draw outside status-control APIs."""
    _emit_statusbar_update(force=True)


@app.route('/api/statusbar', methods=['GET'])
def statusbarApi():
    return jsonify(_status_payload())


@app.route('/api/statusbar/control', methods=['POST'])
def statusbarControlApi():
    payload = request.get_json(silent=True) or {}
    action = str(payload.get('action', '')).strip().lower()

    if action not in ('play', 'stop', 'abort'):
        return jsonify({'error': 'Unknown control action'}), 400

    ok, message, playlist = _playlist_control(action)

    response = {
        'status': 'ok' if ok else 'error',
        'message': message,
        'playlist': playlist,
    }
    _emit_statusbar_update(force=True)
    if not ok:
        return jsonify(response), 409
    return jsonify(response)


@socketio.on('statusbar:subscribe')
def handle_statusbar_subscribe():
    _emit_statusbar_update(force=True, room=request.sid)


@socketio.on('admin:subscribe')
def handle_admin_subscribe():
    _emit_admin_update(room=request.sid)


@socketio.on('statusbar:control')
def handle_statusbar_control(payload):
    payload = payload or {}
    action = str(payload.get('action', '')).strip().lower()

    if action not in ('play', 'stop', 'abort'):
        socketio.emit('statusbar:error', {'error': 'Unknown control action'}, room=request.sid)
        return

    ok, message, playlist = _playlist_control(action)

    if not ok:
        socketio.emit('statusbar:error', {'message': message, 'playlist': playlist}, room=request.sid)

    _emit_statusbar_update(force=True)


_start_status_listener()
