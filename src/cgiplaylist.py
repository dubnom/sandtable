from flask import render_template, request, redirect, url_for
from datetime import datetime

from webapp import app
from cgistuff import cgistuff
import cgistatus
from playlist import Playlist
from playlist_runtime import runner


@app.route('/playlist', methods=['GET', 'POST'])
def playlistPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='playlist'))

    cstuff = cgistuff('Playlist')
    status = ''
    error = ''
    selectedSaved = str(request.values.get('loadname', '') or request.values.get('_loadname', '')).strip() or Playlist.active_name()

    if request.method == 'POST':
        action = request.values.get('action', '')
        if action == 'remove':
            Playlist.remove(request.values.get('id', ''))
            cgistatus._emit_statusbar_update(force=True)
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
            cgistatus._emit_statusbar_update(force=True)
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
        elif action == 'save':
            ok, msg, savedName = Playlist.save_named(request.values.get('_name', ''))
            if ok:
                status = msg
                selectedSaved = savedName
                cgistatus._emit_statusbar_update(force=True)
            else:
                error = msg
        elif action == 'load':
            ok, msg, loadedName = Playlist.load_named(request.values.get('_loadname', ''))
            if ok:
                status = msg
                selectedSaved = loadedName
                cgistatus._emit_statusbar_update(force=True)
            else:
                error = msg
        elif action == 'rename':
            ok, msg, renamedName = Playlist.rename_named(request.values.get('_loadname', ''), request.values.get('_name', ''))
            if ok:
                status = msg
                selectedSaved = renamedName
                cgistatus._emit_statusbar_update(force=True)
            else:
                error = msg
        elif action == 'delete':
            ok, msg = Playlist.delete_named(request.values.get('_loadname', ''))
            if ok:
                status = msg
                selectedSaved = ''
                cgistatus._emit_statusbar_update(force=True)
            else:
                error = msg
    elif selectedSaved:
        ok, msg, loadedName = Playlist.load_named(selectedSaved)
        if ok:
            status = msg
            selectedSaved = loadedName
        else:
            error = msg

    items = Playlist.list()
    savedPlaylists = Playlist.list_saved()
    if (not selectedSaved or selectedSaved not in savedPlaylists) and savedPlaylists:
        selectedSaved = savedPlaylists[0]
    for item in items:
        try:
            item['createdText'] = datetime.fromtimestamp(int(item.get('created', 0))).strftime('%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError, OSError):
            item['createdText'] = str(item.get('created', ''))

        imageFile = str(item.get('imageFile', '') or '').strip()
        if imageFile:
            item['imageUrl'] = 'store/%s' % imageFile
        else:
            item['imageUrl'] = ''

    return ''.join([
        cstuff.standardTopStr(),
        render_template('playlist-page.tpl', items=items, status=status, error=error, savedPlaylists=savedPlaylists, selectedSaved=selectedSaved),
        cstuff.endBodyStr()])
