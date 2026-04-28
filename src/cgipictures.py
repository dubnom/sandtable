from flask import request, render_template, redirect, url_for
import os
from Sand import PICTURE_PATH
from webapp import app
from cgistuff import cgistuff


@app.route('/pictures', methods=['GET', 'POST'])
def picturesPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='pictures'))

    form = request.form
    action = form.get('action', '').lower()
    if action == 'upload':
        upload = request.files.get('_file')
        if upload is not None:
            name, ext = os.path.splitext(upload.filename)
            if ext in ('.png', '.jpg', '.jpeg', '.gif'):
                upload.save(os.path.join(PICTURE_PATH, upload.filename))

    cstuff = cgistuff('Pictures')

    path = PICTURE_PATH
    dirlist = os.listdir(path)
    dirlist.sort()
    pictures = []
    for f in dirlist:
        filename = os.path.join(path, f)
        if not f.startswith('.') and not os.path.isdir(filename):
            pictures.append((f, filename))

    return ''.join([
        cstuff.standardTopStr(),
        render_template('pictures-page.tpl', pictures=pictures, columns=4),
        cstuff.endBodyStr()])
