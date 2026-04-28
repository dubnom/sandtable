import base64

from flask import request, render_template, jsonify
from datetime import timedelta
from os import stat

from Sand import TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS,\
    MACHINE_UNITS, MACHINE_FEED, MACHINE_ACCEL,\
    IMAGE_TYPE, IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT,\
    CACHE_ENABLE, DATA_PATH, STORE_PATH, drawers
from sandable import sandableFactory, SandException
from Chains import Chains
from webapp import app, socketio
from cgistuff import cgistuff
from dialog import Dialog
from history import History, Memoize

import convert
import mach
import schedapi


def _load_requested_sandable(form):
    """Resolve the selected drawing method using existing load/method behavior."""
    params = None
    action = form.get('action', '')
    if action == 'load' or action == 'Load':
        name = form.get('_loadname', '')
        params = History.load(name)
        sandable = params.sandable
    else:
        sandable = form.get('method', '') or request.args.get('method', '') or drawers[0]
    return sandable, params


def _normalize_sandable(sandable):
    return sandable if sandable in drawers else None


def _json_safe(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if hasattr(value, '__dict__'):
        return {k: _json_safe(v) for k, v in value.__dict__.items() if not k.startswith('_')}
    return str(value)


def _field_to_schema(field):
    kind = type(field).__name__
    schema = {
        'kind': kind,
        'name': getattr(field, 'name', ''),
        'prompt': getattr(field, 'prompt', ''),
        'units': getattr(field, 'units', ''),
        'default': _json_safe(getattr(field, 'default', None)),
    }

    for key in ['min', 'max', 'slider', 'step', 'format', 'length', 'rows', 'cols', 'rbutton']:
        if hasattr(field, key):
            schema[key] = _json_safe(getattr(field, key))

    if hasattr(field, 'list'):
        schema['choices'] = _json_safe(getattr(field, 'list'))
    if hasattr(field, 'filters'):
        schema['filters'] = _json_safe(getattr(field, 'filters'))
    if hasattr(field, 'extensions'):
        schema['extensions'] = bool(getattr(field, 'extensions'))
    if hasattr(field, 'fields'):
        schema['fields'] = [_field_to_schema(child) for child in getattr(field, 'fields')]

    return schema


def _params_payload(editor, params):
    payload = {}
    for field in editor:
        name = getattr(field, 'name', '')
        if not name:
            continue
        if hasattr(params, name):
            payload[name] = _json_safe(getattr(params, name))
    return payload


def _generate_chains_and_image(sandable, sand, params, boundingBox):
    errors = None
    memoize = Memoize()
    if CACHE_ENABLE and memoize.match(sandable, params):
        chains = memoize.chains()
    else:
        try:
            chains = sand.generate(params)
        except SandException as e:
            errors = str(e)
            chains = []
        Chains.saveImage(chains, boundingBox, IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_TYPE, clipToTable=True)
        memoize.save(sandable, params, chains)
    return chains, errors


def _draw_summary(chains, sandable):
    boundingChains = Chains.bound(chains, [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)])
    machChains = Chains.convertUnits(boundingChains, TABLE_UNITS, MACHINE_UNITS)
    seconds, distance, pointCount = Chains.estimateMachiningTime(machChains, MACHINE_FEED, MACHINE_ACCEL)
    drawinfo = 'Draw time %s   %.1f %s   Points %d' % (
        timedelta(0, int(seconds)),
        convert.convert(distance, MACHINE_UNITS, TABLE_UNITS), TABLE_UNITS,
        pointCount)
    helpUrl = 'dhelp/%s' % sandable
    return {
        'seconds': int(seconds),
        'distance': convert.convert(distance, MACHINE_UNITS, TABLE_UNITS),
        'distanceUnits': TABLE_UNITS,
        'pointCount': pointCount,
        'drawinfo': drawinfo,
        'helpUrl': helpUrl,
    }


def _api_prepare_draw(payload):
    method = payload.get('method', request.args.get('method', drawers[0]))
    sandable = _normalize_sandable(method)
    if not sandable:
        return None, jsonify({
            'error': '"%s" is not a valid drawing method!' % method,
            'methods': drawers,
        }), 400

    form = payload.get('form')
    if not isinstance(form, dict):
        form = payload.get('params')
    if not isinstance(form, dict):
        form = {}

    sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
    d = Dialog(sand.editor, form, None)
    params = d.getParams()

    action = payload.get('action', 'refresh')
    if action == 'random' or action == 'Random!':
        params.randomize(sand.editor)

    boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
    chains, errors = _generate_chains_and_image(sandable, sand, params, boundingBox)
    summary = _draw_summary(chains, sandable)
    imageHash = params.hash()

    state = {
        'method': sandable,
        'action': action,
        'sand': sand,
        'dialog': d,
        'paramsObj': params,
        'params': _params_payload(sand.editor, params),
        'chains': chains,
        'errors': errors,
        'fieldErrors': d.errors,
        'boundingBox': boundingBox,
        'summary': summary,
        'image': {
            'path': IMAGE_FILE,
            'hash': imageHash,
            'url': '%s?%s' % (IMAGE_FILE, imageHash),
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
        },
    }
    return state, None, None


def _api_name_error(name):
    if any(k in name for k in './\\~'):
        return '"%s" cannot contain path characters ("./\\~")' % name
    if not len(name):
        return 'No name was specified'
    return None


def _history_items(names):
    items = []
    for name in names:
        png = '%s%s.png' % (STORE_PATH, name)
        try:
            mtime = int(stat(png).st_mtime)
        except OSError:
            continue
        items.append({'name': name, 'path': '%s%s.png?%d' % (STORE_PATH, name, mtime), 'mtime': mtime})
    return items


def _image_data_url(path):
    try:
        with open(path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('ascii')
    except OSError:
        return None
    return 'data:image/png;base64,%s' % encoded


def _api_response_from_state(state, includeFields=False, includeImageData=False):
    payload = {
        'method': state['method'],
        'action': state['action'],
        'errors': state['errors'],
        'fieldErrors': state['fieldErrors'],
        'params': state['params'],
        'image': state['image'],
        'summary': state['summary'],
    }
    if includeImageData:
        imageDataUrl = _image_data_url(state['image']['path'])
        if imageDataUrl:
            payload['image']['dataUrl'] = imageDataUrl
    if includeFields:
        payload['fields'] = [_field_to_schema(field) for field in state['sand'].editor]
    return payload


@app.route('/api/draw/methods', methods=['GET'])
def drawMethodsApi():
    selected = request.args.get('method', drawers[0])
    if selected not in drawers:
        selected = drawers[0]
    return jsonify({
        'methods': drawers,
        'selected': selected,
    })


@app.route('/api/draw/schema', methods=['GET'])
def drawSchemaApi():
    method = request.args.get('method', drawers[0])
    sandable = _normalize_sandable(method)
    if not sandable:
        return jsonify({
            'error': '"%s" is not a valid drawing method!' % method,
            'methods': drawers,
        }), 400

    sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
    return jsonify({
        'method': sandable,
        'fields': [_field_to_schema(field) for field in sand.editor],
        'image': {
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
            'path': IMAGE_FILE,
        },
    })


@socketio.on('draw:schema')
def handle_schema(payload):
    """WebSocket handler for schema request (equivalent to GET /api/draw/schema)."""
    payload = payload or {}
    method = payload.get('method', drawers[0])
    sandable = _normalize_sandable(method)
    if not sandable:
        socketio.emit('draw:schema:response', {
            'error': '"%s" is not a valid drawing method!' % method,
            'methods': drawers,
            'status': 400,
        })
        return

    sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
    socketio.emit('draw:schema:response', {
        'method': sandable,
        'fields': [_field_to_schema(field) for field in sand.editor],
        'image': {
            'path': IMAGE_FILE,
            'hash': None,
            'url': IMAGE_FILE,
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
        },
    })


@app.route('/api/draw/preview', methods=['POST'])
def drawPreviewApi():
    payload = request.get_json(silent=True) or {}
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        return errorResponse, status

    return jsonify(_api_response_from_state(state))


@app.route('/api/draw/history', methods=['GET'])
def drawHistoryApi():
    save, history = History.list()
    return jsonify({
        'saved': _history_items(save),
        'history': _history_items(history),
    })


@app.route('/api/draw/load', methods=['POST'])
def drawLoadApi():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        return jsonify({'error': nameError}), 400

    try:
        loadedParams = History.load(name)
    except OSError:
        return jsonify({'error': 'Unable to load drawing "%s"' % name}), 404

    sandable = _normalize_sandable(getattr(loadedParams, 'sandable', None))
    if not sandable:
        return jsonify({'error': 'Loaded drawing has an invalid drawing method'}), 400

    sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
    d = Dialog(sand.editor, {}, loadedParams)
    params = d.getParams()

    boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
    chains, errors = _generate_chains_and_image(sandable, sand, params, boundingBox)
    summary = _draw_summary(chains, sandable)
    imageHash = params.hash()

    state = {
        'method': sandable,
        'action': 'load',
        'sand': sand,
        'dialog': d,
        'paramsObj': params,
        'params': _params_payload(sand.editor, params),
        'chains': chains,
        'errors': errors,
        'fieldErrors': d.errors,
        'boundingBox': boundingBox,
        'summary': summary,
        'image': {
            'path': IMAGE_FILE,
            'hash': imageHash,
            'url': '%s?%s' % (IMAGE_FILE, imageHash),
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
        },
    }

    response = _api_response_from_state(state, includeFields=True)
    response['loadedName'] = name
    return jsonify(response)


@app.route('/api/draw/execute', methods=['POST'])
def drawExecuteApi():
    payload = request.get_json(silent=True) or {}
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        return errorResponse, status
    if state['errors']:
        return jsonify({
            'error': state['errors'],
            'fieldErrors': state['fieldErrors'],
            'image': state['image'],
            'summary': state['summary'],
        }), 400

    with schedapi.schedapi() as sched:
        sched.demoHalt()
    History.history(state['paramsObj'], state['method'], state['chains'])
    with mach.mach() as e:
        e.run(state['chains'], state['boundingBox'], MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS)

    return jsonify({
        'status': 'ok',
        'method': state['method'],
        'image': state['image'],
        'summary': state['summary'],
    })


@app.route('/api/draw/abort', methods=['POST'])
def drawAbortApi():
    with schedapi.schedapi() as sched:
        sched.demoHalt()
    with mach.mach() as e:
        e.stop()
    return jsonify({'status': 'ok'})


@app.route('/api/draw/save', methods=['POST'])
def drawSaveApi():
    payload = request.get_json(silent=True) or {}
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        return errorResponse, status

    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        return jsonify({
            'error': nameError,
            'image': state['image'],
            'summary': state['summary'],
        }), 400

    History.save(state['paramsObj'], state['method'], state['chains'], name)
    return jsonify({
        'status': 'ok',
        'name': name,
        'image': state['image'],
        'summary': state['summary'],
    })


@app.route('/api/draw/export', methods=['POST'])
def drawExportApi():
    payload = request.get_json(silent=True) or {}
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        return errorResponse, status

    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        return jsonify({
            'error': nameError,
            'image': state['image'],
            'summary': state['summary'],
        }), 400

    fileName = "%s%s.svg" % (DATA_PATH, name)
    Chains.makeSVG(state['chains'], fileName)
    return jsonify({
        'status': 'ok',
        'name': name,
        'file': fileName,
        'image': state['image'],
        'summary': state['summary'],
    })


@app.route('/', methods=['GET'])
@app.route('/draw', methods=['GET', 'POST'])
def drawPage():
    if request.method == 'GET':
        cstuff = cgistuff('Draw')
        selected = request.args.get('method', drawers[0])
        if selected not in drawers:
            selected = drawers[0]
        return ''.join([
            cstuff.standardTopStr(),
            render_template('draw-static-page.tpl', method=selected, sandables=drawers, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, imagefile=IMAGE_FILE),
            cstuff.endBodyStr()])

    cstuff = cgistuff('Draw')
    form = request.values

    # Check to see if params are being loaded from a file
    sandable, params = _load_requested_sandable(form)

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
        chains, genErrors = _generate_chains_and_image(sandable, sand, params, boundingBox)
        if genErrors:
            errors = genErrors

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
            name = form.get('_name', '').strip()
            if any(k in name for k in './\\~'):
                errors = '"%s" cannot contain path characters ("./\\~")' % name
            elif not len(name):
                errors = 'No name was specified'
            else:
                History.save(params, sandable, chains, name)

        # If 'Export' has been requested, export to an SVG file
        if action == 'export' or action == 'Export':
            name = form.get('_name', '').strip()
            if any(k in name for k in './\\~'):
                errors = '"%s" cannot contain path characters ("./\\~")' % name
            elif not len(name):
                errors = 'No name was specified'
            else:
                Chains.makeSVG(chains, "%s%s.svg" % (DATA_PATH, name))

        # Estimate the amount of time it will take to draw
        summary = _draw_summary(chains, sandable)
        help = '' if not sand.__doc__ else '&nbsp;&nbsp;&nbsp;&nbsp;<span class="navigation"><a href="dhelp/%s" target="_blank">Help!</a></span>' % sandable
        drawinfo = 'Draw time %s &nbsp;&nbsp;&nbsp; %.1f %s &nbsp;&nbsp;&nbsp; Points %d' % (
            timedelta(0, summary['seconds']),
            summary['distance'], TABLE_UNITS,
            summary['pointCount'])

        # Make the form
        editor = render_template('draw-form.tpl', sandable=sandable, dialog=d.html(), drawinfo=drawinfo, help=help)
    else:
        errors = '"%s" is not a valid drawing method!' % sandable

    # The hash is used to ensure that cached images are correct
    imageHash = params.hash() if params and hasattr(params, 'hash') else '0'
    imagefile = "%s?%s" % (IMAGE_FILE, imageHash)

    return ''.join([
        cstuff.standardTopStr(),
        render_template('draw-page.tpl', sandables=drawers, sandable=sandable, imagefile=imagefile, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, errors=errors, editor=editor),
        cstuff.endBodyStr()])


# WebSocket event handlers for interactive drawing requests
@socketio.on('draw:preview')
def handle_preview(payload):
    """WebSocket handler for preview request (equivalent to POST /api/draw/preview)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:preview:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        })
        return

    socketio.emit('draw:preview:response', _api_response_from_state(state, includeImageData=True))


@socketio.on('draw:execute')
def handle_execute(payload):
    """WebSocket handler for execute request (equivalent to POST /api/draw/execute)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:execute:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        })
        return
    if state['errors']:
        socketio.emit('draw:execute:response', {
            'error': state['errors'],
            'fieldErrors': state['fieldErrors'],
            'image': state['image'],
            'summary': state['summary'],
            'status': 'error',
        })
        return

    with schedapi.schedapi() as sched:
        sched.demoHalt()
    History.history(state['paramsObj'], state['method'], state['chains'])
    with mach.mach() as e:
        e.run(state['chains'], state['boundingBox'], MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS)

    socketio.emit('draw:execute:response', {
        'status': 'ok',
        'method': state['method'],
        'image': dict(state['image'], dataUrl=_image_data_url(state['image']['path'])),
        'summary': state['summary'],
    })


@socketio.on('draw:abort')
def handle_abort(payload):
    """WebSocket handler for abort request (equivalent to POST /api/draw/abort)"""
    with schedapi.schedapi() as sched:
        sched.demoHalt()
    with mach.mach() as e:
        e.stop()
    socketio.emit('draw:abort:response', {'status': 'ok'})


@socketio.on('draw:save')
def handle_save(payload):
    """WebSocket handler for save request (equivalent to POST /api/draw/save)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:save:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        })
        return

    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        socketio.emit('draw:save:response', {
            'error': nameError,
            'image': state['image'],
            'summary': state['summary'],
            'status': 'error',
        })
        return

    History.save(state['paramsObj'], state['method'], state['chains'], name)
    socketio.emit('draw:save:response', {
        'status': 'ok',
        'name': name,
        'image': state['image'],
        'summary': state['summary'],
    })


@socketio.on('draw:export')
def handle_export(payload):
    """WebSocket handler for export request (equivalent to POST /api/draw/export)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:export:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        })
        return

    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        socketio.emit('draw:export:response', {
            'error': nameError,
            'image': state['image'],
            'summary': state['summary'],
            'status': 'error',
        })
        return

    fileName = "%s%s.svg" % (DATA_PATH, name)
    Chains.makeSVG(state['chains'], fileName)
    socketio.emit('draw:export:response', {
        'status': 'ok',
        'name': name,
        'file': fileName,
        'image': state['image'],
        'summary': state['summary'],
    })
