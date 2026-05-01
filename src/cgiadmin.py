from flask import request, render_template, redirect, url_for
import signal
from html import escape
import os

from Sand import TABLE_WIDTH, TABLE_LENGTH, TABLE_UNITS, BALL_SIZE,\
    MACHINE, MACHINE_FEED, MACHINE_ACCEL, MACHINE_UNITS,\
    MACH_LOG, LED_LOG, SERVER_LOG, SCHEDULER_LOG, MOVIE_STATUS_LOG,\
    VER_FILE, get_image_type, set_image_type, IMAGE_TYPES
from webapp import app
import mach
import convert
import ledapi
import schedapi
import MovieStatus
import cgistatus
from cgistuff import cgistuff


def _format_duration(seconds):
    total = int(max(0, seconds or 0))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return '%d:%02d:%02d' % (hours, minutes, secs)
    return '%d:%02d' % (minutes, secs)


@app.route('/admin/status', methods=['GET', 'POST'])
def status():
    return {'stuff': _status_rows()}


def _status_rows():
    results = [
        ('Table Width',     '%g %s' % (TABLE_WIDTH, TABLE_UNITS)),
        ('Table Length',    '%g %s' % (TABLE_LENGTH, TABLE_UNITS)),
        ('Ball Diameter',   '%g %s' % (BALL_SIZE, TABLE_UNITS)),
        ('Machine Type',    MACHINE),
        ('Machine Feed',    '%g %s' % (MACHINE_FEED, MACHINE_UNITS)),
        ('Machine Accel',   '%g %s' % (MACHINE_ACCEL, MACHINE_UNITS)),
    ]

    try:
        payload = cgistatus._status_payload()
        machineStatus = payload.get('machine', {})
        rawStatus = machineStatus.get('raw', {}) if isinstance(machineStatus, dict) else {}
        drawingStatus = payload.get('drawing', {}) if isinstance(payload, dict) else {}
        playlistStatus = payload.get('playlist', {}) if isinstance(payload, dict) else {}
        if rawStatus:
            results.append(['Machine State', 'Ready' if rawStatus.get('ready') else 'Busy'])
            results.append(['Machine Position', '%.2f, %.2f %s' % (
                rawStatus['pos'][0],
                rawStatus['pos'][1],
                MACHINE_UNITS)])
            results.append(['Table Position', '%.2f, %.2f %s' % (
                convert.convert(rawStatus['pos'][0], MACHINE_UNITS, TABLE_UNITS),
                convert.convert(rawStatus['pos'][1], MACHINE_UNITS, TABLE_UNITS),
                TABLE_UNITS)])
            if drawingStatus.get('state') == 'running':
                results.append(['Current Drawing', drawingStatus.get('title') or drawingStatus.get('method') or 'Drawing'])
                if drawingStatus.get('percentComplete') is not None:
                    results.append(['Drawing Progress', '%.1f%%' % drawingStatus['percentComplete']])
                results.append(['Elapsed', _format_duration(drawingStatus.get('elapsedSeconds', 0))])
                results.append(['Remaining', _format_duration(drawingStatus.get('remainingSeconds', 0))])
                if drawingStatus.get('pointCount'):
                    results.append(['Point Count', '%d' % drawingStatus['pointCount']])
            elif 'percent' in rawStatus:
                results.append(['Queue Progress', '%5.1f%%' % (100 * rawStatus['percent'])])
            results.append(['Playlist Status', '%s - %s' % (
                playlistStatus.get('state', 'unknown'),
                playlistStatus.get('message', ''),
            )])
    except Exception:
        results.append(('State', 'Unknown'))
        results.append(('Position', 'Unknown'))

    try:
        with schedapi.schedapi() as sched:
            results.append(('Demo Mode', '%s' % sched.status()))
    except Exception:
        results.append(('Demo Mode', 'Unknown'))

    try:
        with ledapi.ledapi() as led:
            results.append(('LED Status', '%s' % led.status()))
    except Exception:
        results.append(('LED Status', 'Unknown'))

    results.append(('Movie Status', MovieStatus.MovieStatus().load()))
    return results


@app.route('/admin', methods=['GET', 'POST'])
def adminPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='admin'))

    actions = {
        "server_log":   (_serverLog,    "Server Log - View the web server log"),
        "led_log":      (_ledsLog,      "Led Log - View the ledaemon log (lighting system"),
        "led_res":      (_ledsReset,    "Led Reset - Reset the lighting system"),
        "mach_halt":    (_machHalt,     "Mach Halt - Halt current drawing"),
        "mach_home":    (_home,         "Mach Home - Move ball to (0,0) and recalibrate"),
        "mach_log":     (_machLog,      "Mach Log - View the log of the motor control system"),
        "mach_res":     (_machReset,    "Mach Reset - Reset the motor control system"),
        "mach_res_a":   (_machResetA,   "Mach Reset and Reinitialize - Reset everything motor control related"),
        "sched_log":    (_schedLog,     "Scheduler log - view the log of the demo scheduler"),
        "sched_res":    (_schedReset,   "Scheduler Reset - Reset the scheduler/switch monitor"),
        "demo_cont":    (_schedDemo,    "Demo mode - Go into continuous demonstration mode"),
        "demo_once":    (_schedOnce,    "Demo mode - Single demo"),
        "demo_halt":    (_schedHalt,    "Demo mode - Exit"),
        "movie_log":    (_movieLog,     "Movie Log - View the log of the movie system"),
        "movie_halt":   (_movieHalt,    "Movie Halt - Stop the movie system"),
    }

    cstuff = cgistuff('Admin', jQuery=True)

    form = request.form
    action = form.get('action', '')

    if action == 'set_image_type':
        val = form.get('image_type', '')
        if val in IMAGE_TYPES:
            set_image_type(val)
        message, message2 = 'Image type set to %s' % get_image_type(), None
    elif action in actions:
        message, message2 = actions[action][0]()
    else:
        message, message2 = None, None

    return ''.join([
        cstuff.standardTopStr(),
        render_template('admin-page.tpl', message=message, message2=message2, actions=actions,
                        imageType=get_image_type(), imageTypes=IMAGE_TYPES, statusRows=_status_rows()),
        cstuff.endBodyStr()])


def _escapeFile(filename):
    try:
        with open(filename, 'r') as fp:
            msg = escape(fp.read())
    except Exception:
        msg = ''
    return '<pre class="text">' + msg + '</pre>'


def _home():
    with mach.mach() as e:
        e.home()
    return "HOMING THE MACHINE!!!", None


def _machLog():
    return 'machd.log', _escapeFile(MACH_LOG)


def _ledsLog():
    return 'ledaemon.log', _escapeFile(LED_LOG)


def _serverLog():
    return 'server.log', _escapeFile(SERVER_LOG)


def _ledsReset():
    with ledapi.ledapi() as led:
        led.restart()
    return 'Restarting ledaemon', None


def _machHalt():
    with schedapi.schedapi() as sched:
        sched.demoHalt()
    with mach.mach() as e:
        e.stop()
    return 'Halted drawing', None


def _machReset():
    with mach.mach() as e:
        e.restart()
    return 'Restarting machine', None


def _machResetA():
    try:
        with open(VER_FILE, 'w') as f:
            f.truncate()
    except Exception:
        pass
    return _machReset()


def _schedLog():
    return "scheduler.log", _escapeFile(SCHEDULER_LOG)


def _schedReset():
    with schedapi.schedapi() as sched:
        sched.restart()
    return 'Restarting scheduler', None


def _schedOnce():
    with schedapi.schedapi() as sched:
        sched.demoOnce()
    return 'Single Demo Mode', None


def _schedDemo():
    with schedapi.schedapi() as sched:
        sched.demoContinuous()
    return 'Continuous Demo Mode', None


def _schedHalt():
    with schedapi.schedapi() as sched:
        sched.demoHalt()
    return 'Halting Demo Mode', None


def _movieLog():
    ms = MovieStatus.MovieStatus()
    ms.load()
    return str(ms), _escapeFile(MOVIE_STATUS_LOG)


def _movieHalt():
    ms = MovieStatus.MovieStatus()
    ms.load()
    try:
        os.kill(ms.pid, signal.SIGSEGV)
    except Exception:
        pass
    with mach.mach() as e:
        e.stop()
    return 'Movie Halt has been requested', None
