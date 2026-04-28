from flask import jsonify, request
from threading import Lock

from webapp import app, socketio
from playlist_runtime import runner
import mach


_statusMonitorLock = Lock()
_statusMonitorStarted = False
_lastStatusSnapshot = None


def _status_payload():
    machineStatus = {
        'state': 'unknown',
        'ready': None,
        'message': 'Machine status unavailable',
    }
    try:
        with mach.mach() as engine:
            status = engine.getStatus() or {}
        ready = bool(status.get('ready')) if 'ready' in status else None
        machineStatus = {
            'state': 'ready' if ready else 'busy',
            'ready': ready,
            'message': 'Ready' if ready else 'Busy',
            'raw': status,
        }
    except Exception as e:
        machineStatus['message'] = str(e)

    return {
        'machine': machineStatus,
        'playlist': runner.status(),
    }


def _emit_statusbar_update(force=False, room=None):
    global _lastStatusSnapshot
    payload = _status_payload()
    if room is not None:
        socketio.emit('statusbar:update', payload, room=room)
        return payload
    if force or payload != _lastStatusSnapshot:
        _lastStatusSnapshot = payload
        socketio.emit('statusbar:update', payload)
    return payload


def _status_monitor():
    while True:
        try:
            _emit_statusbar_update()
        except Exception:
            pass
        socketio.sleep(2.0)


def _ensure_status_monitor_started():
    global _statusMonitorStarted
    with _statusMonitorLock:
        if _statusMonitorStarted:
            return
        _statusMonitorStarted = True
        socketio.start_background_task(_status_monitor)


@app.route('/api/statusbar', methods=['GET'])
def statusbarApi():
    return jsonify(_status_payload())


@app.route('/api/statusbar/control', methods=['POST'])
def statusbarControlApi():
    payload = request.get_json(silent=True) or {}
    action = str(payload.get('action', '')).strip().lower()

    if action == 'play':
        ok, message = runner.start_all()
    elif action == 'stop':
        ok, message = runner.stop()
    elif action == 'abort':
        ok, message = runner.abort()
    else:
        return jsonify({'error': 'Unknown control action'}), 400

    response = {
        'status': 'ok' if ok else 'error',
        'message': message,
        'playlist': runner.status(),
    }
    _emit_statusbar_update(force=True)
    if not ok:
        return jsonify(response), 409
    return jsonify(response)


@socketio.on('statusbar:subscribe')
def handle_statusbar_subscribe():
    _ensure_status_monitor_started()
    _emit_statusbar_update(force=True, room=request.sid)


@socketio.on('statusbar:control')
def handle_statusbar_control(payload):
    payload = payload or {}
    action = str(payload.get('action', '')).strip().lower()

    if action == 'play':
        ok, message = runner.start_all()
    elif action == 'stop':
        ok, message = runner.stop()
    elif action == 'abort':
        ok, message = runner.abort()
    else:
        socketio.emit('statusbar:error', {'error': 'Unknown control action'}, room=request.sid)
        return

    if not ok:
        socketio.emit('statusbar:error', {'message': message, 'playlist': runner.status()}, room=request.sid)

    _emit_statusbar_update(force=True)
