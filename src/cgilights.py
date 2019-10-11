from bottle import request, route, get, post, template

from Sand import *
from ledstuff import *
from dialog import *
from cgistuff import *

@route('/lights')
@get('/lights')
@post('/lights')
def lightsPage():
    cstuff = cgistuff( 'Lights', jQuery=True )
    form = request.forms

    ledPattern = form.method if form.method in ledPatterns else ledPatterns[0]
    pattern = ledPatternFactory( ledPattern )
    d = Dialog( pattern.editor, form, None, autoSubmit=True )
    params = d.getParams()
    if form.method:
        setLedPattern( pattern, params )

    return [
        cstuff.standardTopStr(),
        template( 'lights-page', pattern=ledPattern, ledPatterns=ledPatterns, editor=d.html()),
        cstuff.endBodyStr() ]
