import base64
from threading import Lock

from flask import request, render_template, jsonify, redirect, url_for
from datetime import timedelta
from os import stat

from Sand import TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS,\
    MACHINE_UNITS, MACHINE_FEED, MACHINE_ACCEL,\
    IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT,\
    CACHE_ENABLE, DATA_PATH, drawers, get_image_type
from sandable import sandableFactory, SandException
from Chains import Chains
from webapp import app, socketio, PROJECT_ROOT
from cgistuff import cgistuff
from dialog import Dialog
from history import History, Memoize
from playlist import Playlist

import convert
import mach
import cgistatus


_previewRequestLock = Lock()
_latestPreviewRequestBySid = {}


def _set_latest_preview_request_id(sid, requestId):
    with _previewRequestLock:
        _latestPreviewRequestBySid[sid] = requestId


def _is_latest_preview_request_id(sid, requestId):
    # Requests without requestId are treated as non-cancelable legacy requests.
    if requestId is None:
        return True
    with _previewRequestLock:
        return _latestPreviewRequestBySid.get(sid) == requestId


def _clear_latest_preview_request_id(sid):
    with _previewRequestLock:
        _latestPreviewRequestBySid.pop(sid, None)


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
        'randomizable': bool(field.isRandomizable()) if hasattr(field, 'isRandomizable') else False,
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
    
    # For DialogFont fields, include the list of available fonts
    if kind == 'DialogFont' and hasattr(field, '_getFonts'):
        fonts = field._getFonts()
        schema['choices'] = [[display, path] for display, path in fonts]

    # For DialogFileList fields, include the flat file list as [display, path] pairs
    if kind == 'DialogFileList' and hasattr(field, '_getFiles'):
        schema['choices'] = [[display, path] for display, path in field._getFiles()]

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


def _generate_chains_and_image(sandable, sand, params, boundingBox, shouldSave=None):
    errors = None
    cancelled = False

    # Drop superseded preview requests before spending CPU on generation.
    if shouldSave is not None and not shouldSave():
        cancelled = True
        return [], errors, cancelled

    memoize = Memoize()
    if CACHE_ENABLE and memoize.match(sandable, params):
        chains = memoize.chains()
    else:
        try:
            chains = sand.generate(params)
        except SandException as e:
            errors = str(e)
            chains = []

        if shouldSave is not None and not shouldSave():
            cancelled = True
            return chains, errors, cancelled

        Chains.saveImage(chains, boundingBox, IMAGE_FILE, IMAGE_WIDTH, IMAGE_HEIGHT, get_image_type(), clipToTable=True)
        memoize.save(sandable, params, chains)
    return chains, errors, cancelled


def _draw_summary(chains, sandable):
    boundingChains = Chains.bound(chains, [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)])
    machChains = Chains.convertUnits(boundingChains, TABLE_UNITS, MACHINE_UNITS)
    seconds, distance, pointCount = Chains.estimateMachiningTime(machChains, MACHINE_FEED, MACHINE_ACCEL)
    drawinfo = 'Draw time %s   %.0f %s   Points %d' % (
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


def _draw_status_meta(method, summary=None, source='draw'):
    payload = {
        'title': str(method),
        'method': str(method),
        'source': source,
    }
    if isinstance(summary, dict) and 'seconds' in summary:
        payload['estimatedSeconds'] = int(summary['seconds'])
    return payload


def _save_playlist_item_image(itemId, imageFile, imagePath, chains, boundingBox):
    try:
        Chains.saveImage(
            chains,
            boundingBox,
            imagePath,
            int(IMAGE_WIDTH / 2),
            int(IMAGE_HEIGHT / 2),
            get_image_type(),
            clipToTable=True,
        )
        Playlist.setImage(itemId, imageFile)
    except Exception:
        app.logger.exception('Failed to generate playlist thumbnail for item %s', itemId)


def _api_prepare_draw(payload, shouldSave=None):
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

    # If a file-list field is empty, pick the first available file so methods like
    # Clipart/Sisyphus render a preview immediately after switching methods.
    for field in sand.editor:
        fieldName = getattr(field, 'name', '')
        if not fieldName or not hasattr(field, '_getFiles'):
            continue
        if params.get(fieldName):
            continue
        files = field._getFiles()
        if files:
            params[fieldName] = files[0][1]

    action = payload.get('action', 'refresh')
    if action == 'random' or action == 'Random!':
        params.randomize(sand.editor)
    elif action == 'random-field':
        fieldName = payload.get('fieldName', '')
        for field in sand.editor:
            if getattr(field, 'name', '') != fieldName:
                continue
            value = field._random()
            if value is not None:
                params[fieldName] = value
            break

    boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
    chains, errors, cancelled = _generate_chains_and_image(sandable, sand, params, boundingBox, shouldSave=shouldSave)
    if cancelled:
        return {
            'cancelled': True,
            'method': sandable,
            'action': action,
        }, None, None

    summary = _draw_summary(chains, sandable)
    imageHash = params.hash()

    state = {
        'method': sandable,
        'action': action,
        'realtime': bool(sand.isRealtime()),
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


def _history_items(names, mutable=False, history=False):
    items = []
    for name in names:
        png = History.image_path(name, history=history)
        try:
            mtime = int(stat(png).st_mtime)
        except OSError:
            continue
        path = History.image_url(name, history=history)
        if mutable:
            path = '%s?%d' % (path, mtime)
        items.append({'name': name, 'path': path, 'mtime': mtime})
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
        'realtime': bool(state.get('realtime', True)),
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
        'realtime': bool(sand.isRealtime()),
        'fields': [_field_to_schema(field) for field in sand.editor],
        'image': {
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
            'path': IMAGE_FILE,
        },
    })


@app.route('/api/draw/schemas', methods=['GET'])
def drawSchemasApi():
    schemas = {}
    for sandable in drawers:
        sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
        schemas[sandable] = {
            'method': sandable,
            'realtime': bool(sand.isRealtime()),
            'fields': [_field_to_schema(field) for field in sand.editor],
            'image': {
                'width': IMAGE_WIDTH,
                'height': IMAGE_HEIGHT,
                'path': IMAGE_FILE,
            },
        }
    return jsonify(schemas)


@app.route('/api/draw/images', methods=['GET'])
def drawImagesApi():
    images = {}
    images_dir = PROJECT_ROOT / 'images'
    for sandable in drawers:
        path = images_dir / ('%s.png' % sandable)
        try:
            with open(path, 'rb') as f:
                images[sandable] = 'data:image/png;base64,' + base64.b64encode(f.read()).decode('ascii')
        except OSError:
            pass
    return jsonify(images)


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
        }, room=request.sid)
        return

    sand = sandableFactory(sandable, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
    socketio.emit('draw:schema:response', {
        'method': sandable,
        'realtime': bool(sand.isRealtime()),
        'fields': [_field_to_schema(field) for field in sand.editor],
        'image': {
            'path': IMAGE_FILE,
            'hash': None,
            'url': IMAGE_FILE,
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
        },
    }, room=request.sid)


@app.route('/api/draw/preview', methods=['POST'])
def drawPreviewApi():
    payload = request.get_json(silent=True) or {}
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        return errorResponse, status
    if state.get('cancelled'):
        return jsonify({'status': 'cancelled'}), 409

    return jsonify(_api_response_from_state(state))


@app.route('/api/draw/history', methods=['GET'])
def drawHistoryApi():
    save, history = History.list()
    return jsonify({
        'saved': _history_items(save, mutable=True, history=False),
        'history': _history_items(history, mutable=False, history=True),
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
    chains, errors, _ = _generate_chains_and_image(sandable, sand, params, boundingBox)
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


@app.route('/api/draw/playlist-item', methods=['POST'])
def drawPlaylistItemApi():
    payload = request.get_json(silent=True) or {}
    itemId = str(payload.get('id', '')).strip()
    if not itemId:
        return jsonify({'error': 'No playlist item id was specified'}), 400

    item = None
    for candidate in Playlist.list():
        if str(candidate.get('id', '')) == itemId:
            item = candidate
            break

    if not item:
        return jsonify({'error': 'Playlist item was not found'}), 404

    state, errorResponse, status = _api_prepare_draw({
        'method': item.get('method', ''),
        'params': item.get('params', {}),
        'action': 'load',
    })
    if errorResponse:
        return errorResponse, status
    if state.get('cancelled'):
        return jsonify({'status': 'cancelled'}), 409

    response = _api_response_from_state(state, includeFields=True)
    response['playlistItemId'] = itemId
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

    History.history(state['paramsObj'], state['method'], state['chains'])
    with mach.mach() as e:
        e.run(state['chains'], state['boundingBox'], MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS, meta=_draw_status_meta(state['method'], state['summary']))
    cgistatus.signal_draw_started()

    return jsonify({
        'status': 'ok',
        'method': state['method'],
        'image': state['image'],
        'summary': state['summary'],
    })


@app.route('/api/draw/abort', methods=['POST'])
def drawAbortApi():
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


@app.route('/draw', methods=['GET', 'POST'])
def drawPage():
    if request.method == 'GET':
        loadName = request.args.get('loadname', '').strip()
        playlistItemId = request.args.get('playlistItemId', '').strip()
        initialParams = {}
        for key, value in request.args.items():
            if key in ('embed', 'view', 'method', 'loadname', 'playlistItemId'):
                continue
            initialParams[key] = value
        if request.args.get('embed') != '1':
            selected = request.args.get('method', drawers[0])
            if selected not in drawers:
                selected = drawers[0]
            redirectArgs = {'view': 'draw', 'method': selected}
            if loadName:
                redirectArgs['loadname'] = loadName
            if playlistItemId:
                redirectArgs['playlistItemId'] = playlistItemId
            redirectArgs.update(initialParams)
            return redirect(url_for('shellPage', **redirectArgs))

        cstuff = cgistuff('Draw')
        selected = request.args.get('method', drawers[0])
        if selected not in drawers:
            selected = drawers[0]
        if playlistItemId:
            for candidate in Playlist.list():
                if str(candidate.get('id', '')) != playlistItemId:
                    continue
                candidateMethod = str(candidate.get('method', '') or '')
                if candidateMethod in drawers:
                    selected = candidateMethod
                candidateParams = candidate.get('params', {})
                if isinstance(candidateParams, dict):
                    initialParams = dict(candidateParams)
                break
        return ''.join([
            cstuff.standardTopStr(),
            render_template('draw-static-page.tpl', method=selected, sandables=drawers, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, embedded=True, loadname=loadName, initial_params=initialParams),
            cstuff.endBodyStr()])

    cstuff = cgistuff('Draw')
    form = request.values
    action = form.get('action', '')
    drawName = form.get('_name', '').strip()
    if action == 'load' or action == 'Load':
        drawName = form.get('_loadname', '').strip()

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
        chains, genErrors, _ = _generate_chains_and_image(sandable, sand, params, boundingBox)
        if genErrors:
            errors = genErrors

        # If 'Draw in Sand' has been requested then do it!
        if action == 'doit' or action == 'Draw in Sand!':
            History.history(params, sandable, chains)
            with mach.mach() as e:
                e.run(chains, boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS, meta=_draw_status_meta(sandable))

        # If 'Abort' has been requested stop the drawing
        if action == 'abort' or action == 'Abort!':
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
        editor = render_template('draw-form.tpl', sandable=sandable, dialog=d.html(), drawinfo=drawinfo, help=help, drawname=drawName)
    else:
        errors = '"%s" is not a valid drawing method!' % sandable

    # The hash is used to ensure that cached images are correct
    imageHash = params.hash() if params and hasattr(params, 'hash') else '0'
    imagefile = "%s?%s" % (IMAGE_FILE, imageHash)

    return ''.join([
        cstuff.standardTopStr(),
        render_template('draw-page.tpl', sandables=drawers, sandable=sandable, imagefile=imagefile, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, errors=errors, editor=editor, drawname=drawName),
        cstuff.endBodyStr()])


# WebSocket event handlers for interactive drawing requests
@socketio.on('draw:preview')
def handle_preview(payload):
    """WebSocket handler for preview request (equivalent to POST /api/draw/preview)"""
    payload = payload if isinstance(payload, dict) else {}
    requestId = payload.get('requestId')
    sid = request.sid
    _set_latest_preview_request_id(sid, requestId)

    state, errorResponse, status = _api_prepare_draw(
        payload,
        shouldSave=lambda: _is_latest_preview_request_id(sid, requestId)
    )

    if not _is_latest_preview_request_id(sid, requestId):
        return

    if errorResponse:
        socketio.emit('draw:preview:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
            'requestId': requestId,
        }, room=request.sid)
        return

    if state.get('cancelled'):
        return

    includeFields = bool(payload.get('includeFields'))
    includeImageData = bool(payload.get('includeImageData'))
    response = _api_response_from_state(state, includeFields=includeFields, includeImageData=includeImageData)
    response['requestId'] = requestId
    socketio.emit('draw:preview:response', response, room=request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    _clear_latest_preview_request_id(request.sid)


@socketio.on('draw:execute')
def handle_execute(payload):
    """WebSocket handler for execute request (equivalent to POST /api/draw/execute)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:execute:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        }, room=request.sid)
        return
    if state['errors']:
        socketio.emit('draw:execute:response', {
            'error': state['errors'],
            'fieldErrors': state['fieldErrors'],
            'image': state['image'],
            'summary': state['summary'],
            'status': 'error',
        }, room=request.sid)
        return

    History.history(state['paramsObj'], state['method'], state['chains'])
    with mach.mach() as e:
        e.run(state['chains'], state['boundingBox'], MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS, meta=_draw_status_meta(state['method'], state['summary']))
    cgistatus.signal_draw_started()

    socketio.emit('draw:execute:response', {
        'status': 'ok',
        'method': state['method'],
        'image': state['image'],
        'summary': state['summary'],
    }, room=request.sid)


@socketio.on('draw:abort')
def handle_abort(payload):
    """WebSocket handler for abort request (equivalent to POST /api/draw/abort)"""
    with mach.mach() as e:
        e.stop()
    socketio.emit('draw:abort:response', {'status': 'ok'}, room=request.sid)


@socketio.on('draw:save')
def handle_save(payload):
    """WebSocket handler for save request (equivalent to POST /api/draw/save)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:save:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        }, room=request.sid)
        return

    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        socketio.emit('draw:save:response', {
            'error': nameError,
            'image': state['image'],
            'summary': state['summary'],
            'status': 'error',
        }, room=request.sid)
        return

    History.save(state['paramsObj'], state['method'], state['chains'], name)
    socketio.emit('draw:save:response', {
        'status': 'ok',
        'name': name,
        'image': state['image'],
        'summary': state['summary'],
    }, room=request.sid)


@socketio.on('draw:export')
def handle_export(payload):
    """WebSocket handler for export request (equivalent to POST /api/draw/export)"""
    state, errorResponse, status = _api_prepare_draw(payload)
    if errorResponse:
        socketio.emit('draw:export:response', {
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
            'status': status,
        }, room=request.sid)
        return

    name = str(payload.get('name', '')).strip()
    nameError = _api_name_error(name)
    if nameError:
        socketio.emit('draw:export:response', {
            'error': nameError,
            'image': state['image'],
            'summary': state['summary'],
            'status': 'error',
        }, room=request.sid)
        return

    fileName = "%s%s.svg" % (DATA_PATH, name)
    Chains.makeSVG(state['chains'], fileName)
    socketio.emit('draw:export:response', {
        'status': 'ok',
        'name': name,
        'file': fileName,
        'image': state['image'],
        'summary': state['summary'],
    }, room=request.sid)


@socketio.on('draw:playlist:add')
def handle_playlist_add(payload):
    """WebSocket handler to add the current drawing configuration to the playlist."""
    payload = payload if isinstance(payload, dict) else {}

    method = _normalize_sandable(payload.get('method', drawers[0]))
    if not method:
        response = {
            'status': 'error',
            'error': 'Invalid drawing method',
        }
        socketio.emit('draw:playlist:add:response', response, room=request.sid)
        return response

    params = payload.get('params')
    if not isinstance(params, dict):
        params = {}

    # Rebuild state via the same parse/validation path used by preview.
    state, errorResponse, status = _api_prepare_draw({
        'method': method,
        'params': params,
        'action': 'refresh',
    })
    if errorResponse:
        response = {
            'status': 'error',
            'error': errorResponse.get_json().get('error') if hasattr(errorResponse, 'get_json') else str(errorResponse),
        }
        socketio.emit('draw:playlist:add:response', response, room=request.sid)
        return response
    if state.get('errors'):
        response = {
            'status': 'error',
            'error': state['errors'],
            'fieldErrors': state.get('fieldErrors', {}),
        }
        socketio.emit('draw:playlist:add:response', response, room=request.sid)
        return response

    item = Playlist.add(state['method'], state['params'])

    imageFile, imagePath = Playlist.image_paths(item['id'])
    item['imageFile'] = imageFile

    response = {
        'status': 'ok',
        'item': item,
        'count': len(Playlist.list()),
    }
    socketio.emit('draw:playlist:add:response', response, room=request.sid)
    cgistatus._emit_statusbar_update(force=True)
    socketio.start_background_task(
        _save_playlist_item_image,
        item['id'],
        imageFile,
        imagePath,
        state['chains'],
        state['boundingBox'],
    )
    return response
