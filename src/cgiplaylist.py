from flask import render_template, request
from datetime import datetime
from os import stat

from webapp import app
from cgistuff import cgistuff
from playlist import Playlist
from playlist_runtime import runner


@app.route('/playlist', methods=['GET', 'POST'])
def playlistPage():
    cstuff = cgistuff('Playlist')
    status = ''
    error = ''

    if request.method == 'POST':
        action = request.values.get('action', '')
        if action == 'remove':
            Playlist.remove(request.values.get('id', ''))
        elif action == 'moveup':
            itemId = request.values.get('id', '')
            if not Playlist.move(itemId, -1):
                error = 'Unable to move item up'
        elif action == 'movedown':
            itemId = request.values.get('id', '')
            if not Playlist.move(itemId, 1):
                error = 'Unable to move item down'
        elif action == 'clear':
            Playlist.clear()
        elif action == 'draw':
            itemId = request.values.get('id', '')
            ok, msg = runner.start_one(itemId)
            if ok:
                status = msg
            else:
                error = msg
        elif action == 'drawall':
            ok, msg = runner.start_all()
            if ok:
                status = msg
            else:
                error = msg

    items = Playlist.list()
    for item in items:
        try:
            item['createdText'] = datetime.fromtimestamp(int(item.get('created', 0))).strftime('%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError, OSError):
            item['createdText'] = str(item.get('created', ''))

        imageFile = str(item.get('imageFile', '') or '').strip()
        if imageFile:
            try:
                mtime = int(stat('store/%s' % imageFile).st_mtime)
            except OSError:
                mtime = 0
            item['imageUrl'] = 'store/%s?%d' % (imageFile, mtime)
        else:
            item['imageUrl'] = ''

    return ''.join([
        cstuff.standardTopStr(),
        render_template('playlist-page.tpl', items=items, status=status, error=error),
        cstuff.endBodyStr()])
