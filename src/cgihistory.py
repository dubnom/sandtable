from bottle import route, template
from os import stat
from Sand import STORE_PATH
from cgistuff import cgistuff
from history import History


@route('/history')
def historyPage():
    cstuff = cgistuff('Drawing History')

    def mtimes(x): return [stat('%s%s.png' % (STORE_PATH, name)).st_mtime for name in x]
    save, history = History.list()

    return [
        cstuff.standardTopStr(),
        template('history-page', save=save, history=history, path=STORE_PATH, mtimes=mtimes),
        cstuff.endBodyStr()]
