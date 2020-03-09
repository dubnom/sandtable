from bottle import request, route, post, get, template
from datetime import timedelta

from Sand import TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS,\
    MACHINE_UNITS, MACHINE_FEED, MACHINE_ACCEL,\
    IMAGE_TYPE, IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT,\
    CACHE_ENABLE, DATA_PATH, drawers
from sandable import sandableFactory, SandException
from Chains import Chains
from cgistuff import cgistuff
from dialog import Dialog
from history import History, Memoize

import convert
import mach
import schedapi


@route('/')
@post('/draw')
@get('/draw')
def drawPage():
    cstuff = cgistuff('Draw')
    form = request.forms

    # Check to see if params are being loaded from a file
    params = None
    action = form.action
    if action == 'load' or action == 'Load':
        name = form._loadname
        params = History.load(name)
        sandable = params.sandable
    else:
        sandable = form.method or request.query.method or drawers[0]

    # Take action
    editor, errors = '', None
    if sandable in drawers:
        sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
        d = Dialog(sand.editor, form, params)
        params = d.getParams()
        action = d.getAction()
        if action == 'random' or action == 'Random!':
            params.randomize(sand.editor)

        # Create the path image
        boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]

        # Generate the chains
        memoize = Memoize()
        if CACHE_ENABLE and memoize.match(sandable, params):
            chains = memoize.chains()
        else:
            try:
                chains = sand.generate(params)
            except SandException as e:
                errors = str(e)
                chains = []
            Chains.saveImage(chains, boundingBox, IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_TYPE)
            memoize.save(sandable, params, chains)

        # If 'Draw in Sand' has been requested then do it!
        if action == 'doit' or action == 'Draw in Sand!':
            with schedapi.schedapi() as sched:
                sched.demoHalt()
            History.history(params, sandable, chains)
            with mach.mach() as e:
                e.run(chains, boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS)

        # If 'Abort' has been requested stop the drawing
        if action == 'abort' or action == 'Abort!':
            with schedapi.schedapi() as sched:
                sched.demoHalt()
            with mach.mach() as e:
                e.stop()

        # If 'Save' has been requested save the drawing's parameters
        if action == 'save' or action == 'Save':
            name = form._name.strip()
            if any(k in name for k in './\\~'):
                errors = '"%s" cannot contain path characters ("./\\~")' % name
            elif not len(name):
                errors = 'No name was specified'
            else:
                History.save(params, sandable, chains, name)

        # If 'Export' has been requested, export to an SVG file
        if action == 'export' or action == 'Export':
            name = form._name.strip()
            if any(k in name for k in './\\~'):
                errors = '"%s" cannot contain path characters ("./\\~")' % name
            elif not len(name):
                errors = 'No name was specified'
            else:
                Chains.makeSVG(chains, "%s%s.svg" % (DATA_PATH, name))

        # Estimate the amount of time it will take to draw
        chains = Chains.bound(chains, boundingBox)
        chains = Chains.convertUnits(chains, TABLE_UNITS, MACHINE_UNITS)
        seconds, distance, pointCount = Chains.estimateMachiningTime(chains, MACHINE_FEED, MACHINE_ACCEL)
        help = '' if not sand.__doc__ else '&nbsp;&nbsp;&nbsp;&nbsp;<span class="navigation"><a href="dhelp/%s" target="_blank">Help!</a></span>' % sandable
        drawinfo = 'Draw time %s &nbsp;&nbsp;&nbsp; %.1f %s &nbsp;&nbsp;&nbsp; Points %d' % (
                timedelta(0, int(seconds)),
                convert.convert(distance, MACHINE_UNITS, TABLE_UNITS), TABLE_UNITS,
                pointCount)

        # Make the form
        editor = template('draw-form', sandable=sandable, dialog=d.html(), drawinfo=drawinfo, help=help)
    else:
        errors = '"%s" is not a valid drawing method!' % sandable

    # The hash is used to ensure that cached images are correct
    imagefile = "%s?%s" % (IMAGE_FILE, params.hash())

    return [
        cstuff.standardTopStr(),
        template('draw-page', sandables=drawers, sandable=sandable, imagefile=imagefile, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, errors=errors, editor=editor),
        cstuff.endBodyStr()]
