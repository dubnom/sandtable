from bottle import request, route, get, post, template
import os
from Sand import PICTURE_PATH
from cgistuff import cgistuff


@route('/pictures')
@get('/pictures')
@post('/pictures')
def picturesPage():
    form = request.forms
    action = form.action.lower() if form.action else ''
    if action == 'upload':
        upload = request.files.get('_file')
        name, ext = os.path.splitext(upload.filename)
        if ext in ('.png', '.jpg', '.jpeg', '.gif'):
            upload.save(PICTURE_PATH)

    cstuff = cgistuff('Pictures')

    path = PICTURE_PATH
    dirlist = os.listdir(path)
    dirlist.sort()
    pictures = []
    for f in dirlist:
        filename = os.path.join(path, f)
        if not f.startswith('.') and not os.path.isdir(filename):
            pictures.append((f, filename))

    return [
        cstuff.standardTopStr(),
        template('pictures-page', pictures=pictures, columns=4),
        cstuff.endBodyStr()]
