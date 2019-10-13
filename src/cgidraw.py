from bottle import request, route, post, get, template
from time import time
from datetime import timedelta

from Sand import *
from Chains import *
from cgistuff import *
from dialog import Dialog
from history import *

import mach
import schedapi

@route('/')
@post('/draw')
@get('/draw')
def drawPage():
    cstuff = cgistuff( 'Draw' )
    form = request.forms
    cfg = LoadConfig()  
 
    # Check to see if params are being loaded from a file
    params = None
    action = form.action
    if action == 'load' or action == 'Load':
        name = form._loadname
        params = History.load( name )
        sandable = params.sandable
    else:
        sandable = form.method or request.query.method or sandables[0]

    # Take action
    editor, errors = '', None 
    if sandable in sandables:
        sand = sandableFactory( sandable )
        d = Dialog( sand.editor, form, params )
        params = d.getParams()
        action = d.getAction()
        if action == 'random' or action == 'Random!':
            params.randomize( sand.editor )

        # Create the path image
        boundingBox = [ (0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH) ]

        # Generate the chains
        memoize = Memoize()
        if cfg.cache and memoize.match( sandable, params ):
            chains = memoize.chains()
        else:
            try:
                chains = sand.generate( params )
            except SandException as e:
                errors = str(e)
                chains = []
            Chains.saveImage( chains, boundingBox, IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT, cfg.imgType )
            memoize.save( sandable, params, chains )

        # If 'Draw in Sand' has been requested then do it!
        if action == 'doit' or action == 'Draw in Sand!':
            with schedapi.schedapi() as sched:
                sched.demoHalt()
            History.history( params, sandable, chains )
            Chains.makeGCode( chains, boundingBox, cfg.maxFeed, GCODE_FILE, MACHINE_UNITS, TABLE_UNITS )
            with mach.mach() as e:
                e.run( GCODE_FILE )

        # If 'Abort' has been requested stop the drawing
        if action == 'abort' or action == 'Abort!':
            with schedapi.schedapi() as sched:
                sched.demoHalt()
            with mach.mach() as e:
                e.stop()

        # If 'Save' has been requested save the drawing's parameters
        if action == 'save' or action == 'Save':
            name = form._name.strip()
            if any( k in name for k in './\\~'):
                errors = '"%s" cannot contain path characters ("./\\~")' % name
            elif not len(name):
                errors = 'No name was specified'
            else:
                History.save( params, sandable, chains, name )

        # If 'Export' has been requested, export to an SVG file
        if action == 'export' or action == 'Export':
            name = form._name.strip()
            if any( k in name for k in './\\~'):
                errors = '"%s" cannot contain path characters ("./\\~")' % name
            elif not len(name):
                errors = 'No name was specified'
            else:
                Chains.makeSVG( chains, "%s%s.svg" % (DATA_PATH, name))

        # Estimate the amount of time it will take to draw
        seconds, distance, pointCount = Chains.estimateMachiningTime( chains, boundingBox, cfg.maxFeed, TABLE_ACCEL )
        help = '' if not sand.__doc__ else '&nbsp;&nbsp;&nbsp;&nbsp;<span class="navigation"><a href="dhelp/%s" target="_blank">Help!</a></span>' % sandable
        drawinfo = 'Draw time %s &nbsp;&nbsp;&nbsp; %.1f feet &nbsp;&nbsp;&nbsp; Points %d' % (timedelta( 0, int( seconds )), distance / 12.0, pointCount)

        # Make the form
        editor = template( 'draw-form', sandable=sandable, dialog=d.html(), drawinfo=drawinfo, help=help)
    else:
        errors = '"%s" is not a valid drawing method!' % sandable

    # The hash is used to ensure that cached images are correct
    imagefile = "%s?%d" % (IMAGE_FILE, hash((sandable,params)))

    return [ 
        cstuff.standardTopStr(),
        template( 'draw-page', sandables=sandables, sandable=sandable, imagefile=imagefile, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, errors=errors, editor=editor ),
        cstuff.endBodyStr() ]
