from bottle import route, template
import markdown

from Sand import drawers, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS
from sandable import sandableFactory


@route('/dhelp/<method>')
def main(method):
    method = method if method in drawers else drawers[0]
    sandable = sandableFactory(method, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
    if sandable:
        doc = markdown.markdown(sandable.__doc__, extensions=['tables']) if sandable.__doc__ else 'No documentation available'
    else:
        doc = '<div class="error">Error "%s" is not a valid drawing method!</div>' % method

    return [template('dhelp-page', method=method, doc=doc)]
