from bottle import request, route, post, get, template
import signal
from cgi import escape
import os

from Sand import *
import mach
import schedapi
import MovieStatus
from cgistuff import *
from dialog import *
from ledstuff import *

@route('/admin/status')     # FIX: Remove this
@post('/admin/status')
def status():
    results = {}
    try:
        with mach.mach() as e:
            results[ 'tableState'   ] = ["Busy","Ready"][e.getState()]
            results[ 'ballPosition' ] = e.getPosition()
            # FIX: type of drawing, Estimated time, estimated remaining time, points, length, remaining points, remaining length
    except:
        results[ 'tableState' ] = 'Unknown'
        results[ 'ballPosition' ] = None

    try:
        with schedapi.schedapi() as sched:
            results[ 'demoMode' ] = sched.status()
    except:
        results[ 'demoMode' ] = { 'state': 'Unknown' }

    try:
        with ledApi() as api:
            results[ 'ledStatus' ] = api.status()
    except:
        results[ 'ledStatus' ] = { 'running': 'Unknown', 'pattern': 'Unknown' }

    results[ 'movieStatus' ] = MovieStatus.MovieStatus().load() 
    return results 


@route('/admin')
@post('/admin')
@get('/admin')
def adminPage():
    cfg = LoadConfig()
    editor = [
        Dialog2Choices( "imgType",      "Image Type",           default = cfg.imgType, list = ['Schematic','Realistic'] ),
        DialogInt(      "maxFeed",      "Maximum Feed Rate",    units = "inches/minute", default = cfg.maxFeed, min = 1.0 ),
        DialogFloat(    "ballSize",     "Ball Size",            units = "inches", default = cfg.ballSize, min = 0.25, max = 2.0 ),
        DialogYesNo(    "cache",        "Enable Cache",         default = cfg.cache ),
        DialogYesNo(    "cgiDebug",     "Show CGI Errors",      default = cfg.cgiDebug ),
        DialogYesNo(    "scheduler",    "Enable Nightly Demos", default = cfg.scheduler ),
    ]
    
    actions = {
            "update":       (_update,       None),
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
            "restore":      (_restoreDef,   "Restore parameters to defaults"),
    }

    cstuff = cgistuff( 'Admin', jQuery=True )

    form = request.forms
    d = Dialog( editor, form, None )
    params = d.getParams()
    action = d.getAction()

    if action in actions:
        message, message2 = actions[ action ][0]( params )
    else:
        message, message2 = None, None
    
    return [
        cstuff.standardTopStr(),
        template( 'admin-page', message=message, message2=message2, form=d.html(), actions=actions ), 
        cstuff.endBodyStr() ] 

def _escapeFile( filename ):
    try:
        with open( filename, 'rt' ) as fp:
            msg = escape( fp.read().decode('utf-8','replace').encode('utf-8'))
    except:
        msg = '' 
    return '<pre class="text">' + msg + '</pre>'

def _home(params):
    with mach.mach() as e:
        e.home()
    return "HOMING THE MACHINE!!!", None

def _machLog(params):
    return 'machd.log', _escapeFile( MACH_LOG ) 
    
def _ledsLog(params):
    return 'ledaemon.log', _escapeFile( LED_LOG )

def _serverLog(params):
    return 'server.log', _escapeFile( SERVER_LOG )

def _machGcode(params):
    return 'G-Code', _escapeFile( GCODE_FILE )

def _update(params):
    cfg = Config();
    cfg.imgType     = params.imgType 
    cfg.maxFeed     = params.maxFeed
    cfg.ballSize    = params.ballSize
    cfg.cache       = params.cache
    cfg.cgiDebug    = params.cgiDebug
    cfg.scheduler   = params.scheduler
    SaveConfig(cfg)
    return 'Updated Parameters', None

def _ledsReset(params):
    with ledApi() as api:
        api.restart()
    return 'Restarting ledaemon', None

def _machReset(params):
    with mach.mach() as e:
        e.restart()
    return 'Restarting machine', None 

def _machResetA(params):
    try:
        with open(VER_FILE,'w') as f:
            f.truncate()
    except:
        pass
    return _machReset(params)

def _schedLog(params):
    return "scheduler.log", _escapeFile( SCHEDULER_LOG )

def _schedReset(params):
    with schedapi.schedapi() as sched:
        sched.restart()
    return 'Restarting scheduler', None

def _schedOnce(params):
    with schedapi.schedapi() as sched:
        sched.demoOnce()
    return 'Single Demo Mode', None

def _schedDemo(params):
    with schedapi.schedapi() as sched:
        sched.demoContinuous()
    return 'Continuous Demo Mode', None

def _schedHalt(params):
    with schedapi.schedapi() as sched:
        sched.demoHalt()
    return 'Halting Demo Mode', None

def _restoreDef(params):
    os.remove( CONFIG_FILE )
    return 'Restoring Sandtable Defaults', None

def _movieLog(params):
    ms = MovieStatus.MovieStatus()
    ms.load()
    return str(ms), _escapeFile( MOVIE_STATUS_LOG ) 

def _movieHalt(params):
    ms = MovieStatus.MovieStatus()
    ms.load()
    try:
        os.kill( ms.pid, signal.SIGSEGV )
    except:
        pass
    with mach.mach() as e:
        e.stop()
    return 'Movie Halt has been requested', None

