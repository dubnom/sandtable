from flask import request, render_template

from Sand import ledPatterns, LED_COLUMNS, LED_ROWS
from dialog import Dialog
from webapp import app
from cgistuff import cgistuff
from ledable import ledPatternFactory
import ledapi


@app.route('/lights', methods=['GET', 'POST'])
def lightsPage():
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
        render_template('lights-page.tpl', pattern=ledPattern, ledPatterns=ledPatterns, editor=d.html()),
        cstuff.endBodyStr()])
