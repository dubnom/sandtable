import base64
from functools import lru_cache

from flask import request, render_template, redirect, url_for

from Sand import ledPatterns, LED_COLUMNS, LED_ROWS
from dialog import Dialog
from webapp import app, PROJECT_ROOT
from cgistuff import cgistuff
from ledable import ledPatternFactory
import ledapi


@lru_cache(maxsize=1)
def _pattern_images_data_urls():
    images = {}
    images_dir = PROJECT_ROOT / 'images'
    for pattern_name in ledPatterns:
        path = images_dir / f'{pattern_name}.png'
        try:
            png_bytes = path.read_bytes()
        except OSError:
            continue
        b64 = base64.b64encode(png_bytes).decode('ascii')
        images[pattern_name] = f'data:image/png;base64,{b64}'
    return images


@app.route('/lights', methods=['GET', 'POST'])
def lightsPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='lights'))

    cstuff = cgistuff('Lights', jQuery=True)
    form = request.form
    formData = dict(form)
    status = None
    try:
        with ledapi.ledapi() as led:
            status = led.status()
    except Exception:
        status = None

    method = form.get('method', '')
    statusPattern = str((status or {}).get('pattern', '') or '')
    statusParams = (status or {}).get('params', {}) if isinstance((status or {}).get('params', {}), dict) else {}

    if method in ledPatterns:
        ledPattern = method
    elif statusPattern in ledPatterns:
        ledPattern = statusPattern
    else:
        ledPattern = ledPatterns[0]

    if method not in ledPatterns and statusParams:
        # No explicit user selection: initialize controls from daemon state.
        for key, value in statusParams.items():
            formData[str(key)] = value

    pattern = ledPatternFactory(ledPattern, LED_COLUMNS, LED_ROWS)
    d = Dialog(pattern.editor, formData, None, autoSubmit=True)
    params = d.getParams()
    if method:
        try:
            with ledapi.ledapi() as led:
                response = led.setPattern(ledPattern, params)
                if isinstance(response, dict):
                    daemonPattern = str(response.get('pattern', '') or '')
                    if daemonPattern in ledPatterns:
                        ledPattern = daemonPattern
        except Exception:
            pass

    return ''.join([
        cstuff.standardTopStr(),
        render_template(
            'lights-page.tpl',
            pattern=ledPattern,
            ledPatterns=ledPatterns,
            patternImages=_pattern_images_data_urls(),
            editor=d.html(),
        ),
        cstuff.endBodyStr()])
