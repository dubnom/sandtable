from flask import render_template
from os import stat
from Sand import STORE_PATH
from webapp import app
from cgistuff import cgistuff
from history import History


@app.route('/history', methods=['GET'])
def historyPage():
    cstuff = cgistuff('Drawing History')

    def mtimes(x): return [stat('%s%s.png' % (STORE_PATH, name)).st_mtime for name in x]
    save, history = History.list()
    save_items = list(zip(save, mtimes(save)))
    history_items = list(zip(history, mtimes(history)))

    return ''.join([
        cstuff.standardTopStr(),
        render_template('history-page.tpl', save_items=save_items, history_items=history_items, path=STORE_PATH),
        cstuff.endBodyStr()])
