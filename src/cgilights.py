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

    method = form.get('method', '')
    ledPattern = method if method in ledPatterns else ledPatterns[0]
    pattern = ledPatternFactory(ledPattern, LED_COLUMNS, LED_ROWS)
    d = Dialog(pattern.editor, form, None, autoSubmit=True)
    params = d.getParams()
    if method:
        with ledapi.ledapi() as led:
            led.setPattern(ledPattern, params)

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
