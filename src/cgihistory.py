from flask import render_template, request, redirect, url_for
from os import stat
from webapp import app
from cgistuff import cgistuff
from history import History


@app.route('/history', methods=['GET'])
def historyPage():
    if request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='history'))

    cstuff = cgistuff('Drawing History')

    save, history = History.list()

    save_items = []
    for name in save:
        png = History.image_path(name, history=False)
        try:
            mtime = int(stat(png).st_mtime)
        except OSError:
            continue
        save_items.append({'name': name, 'path': '%s?%d' % (History.image_url(name, history=False), mtime)})

    history_items = []
    for name in history:
        png = History.image_path(name, history=True)
        try:
            stat(png)
        except OSError:
            continue
        history_items.append({'name': name, 'path': History.image_url(name, history=True)})

    return ''.join([
        cstuff.standardTopStr(),
        render_template('history-page.tpl', save_items=save_items, history_items=history_items),
        cstuff.endBodyStr()])
