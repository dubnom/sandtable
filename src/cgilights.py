from bottle import request, route, get, post, template

from Sand import ledPatterns, LED_COLUMNS, LED_ROWS
from dialog import Dialog
from cgistuff import cgistuff
from ledable import ledPatternFactory
import ledapi


@route('/lights')
@get('/lights')
@post('/lights')
def lightsPage():
    cstuff = cgistuff('Lights', jQuery=True)
    form = request.forms

    ledPattern = form.method if form.method in ledPatterns else ledPatterns[0]
    pattern = ledPatternFactory(ledPattern, LED_COLUMNS, LED_ROWS)
    d = Dialog(pattern.editor, form, None, autoSubmit=True)
    params = d.getParams()
    if form.method:
        with ledapi.ledapi() as led:
            led.setPattern(ledPattern, params)

    return [
        cstuff.standardTopStr(),
        template('lights-page', pattern=ledPattern, ledPatterns=ledPatterns, editor=d.html()),
        cstuff.endBodyStr()]
