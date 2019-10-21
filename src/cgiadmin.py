from bottle import request, route, post, get, template
import signal
from cgi import escape
import os

from Sand import *
import mach
import schedapi
import MovieStatus
from cgistuff import *
from ledstuff import *

@route('/admin/status')     # FIX: Remove this
@post('/admin/status')
def status():
    results = [
        ('Table Width',     '%g %s' % (TABLE_WIDTH, TABLE_UNITS)),
        ('Table Length',    '%g %s' % (TABLE_LENGTH, TABLE_UNITS)),
        ('Ball Diameter',   '%g %s' % (BALL_SIZE, TABLE_UNITS)),
        ('Machine Type',    MACHINE),
        ('Machine Feed',    '%g %s' % (MACHINE_FEED, MACHINE_UNITS)),
        ('Machine Accel',   '%g %s' % (MACHINE_ACCEL, MACHINE_UNITS)),
    ]

    try:
        with mach.mach() as e:
            results.append( [ 'State', ["Busy","Ready"][e.getState()]] )
            results.append( [ 'Position', '%g, %g' %  e.getPosition()] )
            # FIX: type of drawing, Estimated time, estimated remaining time, points, length, remaining points, remaining length
    except:
        results.append( ('State', 'Unknown' ))
        results.append( ('Position', 'Unknown'))

    try:
        with schedapi.schedapi() as sched:
            results.append( ('Demo Mode', '%s' % sched.status()))
    except:
        results.append( ('Demo Mode', 'Unknown'))

    try:
        with ledApi() as api:
            results.append( ('LED Status', '%s' % api.status()))
    except:
        results.append( ('LED Status', 'Unknown'))

    results.append( ('Movie Status', MovieStatus.MovieStatus().load()))
    return {'stuff':results}


@route('/admin')
@post('/admin')
@get('/admin')
def adminPage():
    actions = {
            "server_log":   (_serverLog,    "Server Log - View the web server log"),
            "led_log":      (_ledsLog,      "Led Log - View the ledaemon log (lighting system"),
            "led_res":      (_ledsReset,    "Led Reset - Reset the lighting system"),
            "mach_home":    (_home,         "Mach Home - Move ball to (0,0) and recalibrate"),
            "mach_log":     (_machLog,      "Mach Log - View the log of the motor control system"),
            "mach_gcode":   (_machGcode,    "Mach GCode - View the last instruction file sent to the motor controller"),
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

    cstuff = cgistuff( 'Admin', jQuery=True )

    form = request.forms
    action = form.action

    if action in actions:
        message, message2 = actions[ action ][0]()
    else:
        message, message2 = None, None
    
    return [
        cstuff.standardTopStr(),
        template( 'admin-page', message=message, message2=message2, actions=actions ), 
        cstuff.endBodyStr() ] 

def _escapeFile( filename ):
    try:
        with open( filename, 'r' ) as fp:
            msg = escape(fp.read())
    except:
        msg = '' 
    return '<pre class="text">' + msg + '</pre>'

def _home():
    with mach.mach() as e:
        e.home()
    return "HOMING THE MACHINE!!!", None

def _machLog():
    return 'machd.log', _escapeFile( MACH_LOG ) 
    
def _ledsLog():
    return 'ledaemon.log', _escapeFile( LED_LOG )

def _serverLog():
    return 'server.log', _escapeFile( SERVER_LOG )

def _machGcode():
    return 'G-Code', _escapeFile( GCODE_FILE )

def _ledsReset():
    with ledApi() as api:
        api.restart()
    return 'Restarting ledaemon', None

def _machReset():
    with mach.mach() as e:
        e.restart()
    return 'Restarting machine', None 

def _machResetA():
    try:
        with open(VER_FILE,'w') as f:
            f.truncate()
    except:
        pass
    return _machReset()

def _schedLog():
    return "scheduler.log", _escapeFile( SCHEDULER_LOG )

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
    return str(ms), _escapeFile( MOVIE_STATUS_LOG ) 

def _movieHalt():
    ms = MovieStatus.MovieStatus()
    ms.load()
    try:
        os.kill( ms.pid, signal.SIGSEGV )
    except:
        pass
    with mach.mach() as e:
        e.stop()
    return 'Movie Halt has been requested', None

