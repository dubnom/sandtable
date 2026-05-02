from flask import request, render_template, redirect, url_for
import base64
import os
import logging
from html import escape
from urllib.parse import quote
from Sand import PICTURE_PATH, CLIPART_PATH, THR_PATH, MOVIE_SCRIPT_PATH, STORE_PATH, MOVIE_OUTPUT_PATH
from webapp import app
from cgistuff import cgistuff
from history import History
from thrCache import get_or_create_thumb, warm_cache

warm_cache()


class ftBase():
    def delete(self, f, filename):
        os.remove(filename)
        return (True, 'Deleted')

    def rename(self, f, oldName, newName):
        exts = oldName.split('.')
        newName = os.path.join(self.path, newName + '.' + exts[-1])
        os.rename(oldName, newName)
        return (True, 'Renamed')


class ftPictures(ftBase):
    def __init__(self):
        self.path = PICTURE_PATH
        self.columns = 6
        self.filter = ['png', 'jpg', 'jpeg', 'gif', 'webp']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        url = f"/?view=draw&method=Picture&filename={quote(fn, safe='')}"
        return f'<button class="filer" type="button" onclick="window.location.href=\'{url}\'"><img src="{fn}" width="80" align="center"></button>'


class ftClipart(ftBase):
    def __init__(self):
        self.path = CLIPART_PATH
        self.columns = 6
        self.filter = ['svg']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        src = fn if fn.endswith('.svg') else "images/file.png"
        url = f"/?view=draw&method=Clipart&filename={quote(fn, safe='')}"
        return f'<button class="filer" type="button" onclick="window.location.href=\'{url}\'"><img src="{src}" width="80"></button>'

    def rename(self, f, oldName, newName):
        path = os.path.dirname(oldName)
        exts = oldName.split('.')
        os.rename(os.path.join(path, f + '.' + exts[-1]), os.path.join(path, newName + '.' + exts[-1]))
        return (True, 'Renamed')


class ftSisyphus(ftBase):
    def __init__(self):
        self.path = THR_PATH
        self.columns = 6
        self.filter = ['thr']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        url = f"/?view=draw&method=Sisyphus&filename={quote(fn, safe='')}"
        thumb = get_or_create_thumb(fn)
        img_src = "images/thr.png"
        if thumb:
            try:
                with open(thumb, 'rb') as thumb_file:
                    img_src = 'data:image/png;base64,' + base64.b64encode(thumb_file.read()).decode('ascii')
            except OSError:
                img_src = thumb
        return f'<button class="filer" type="button" onclick="window.location.href=\'{url}\'"><img src="{img_src}" width="80"></button>'

class ftScripts(ftBase):
    def __init__(self):
        self.path = MOVIE_SCRIPT_PATH
        self.columns = 6
        self.filter = ['xml']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
           return f"""<button class="filer" type="button" onclick="window.location.href='/?view=movie&loadname={quote(p[0], safe='')}'">
               <img src="images/script.png" width="80">
               </button>"""


class ftMovies(ftBase):
    def __init__(self):
        self.path = MOVIE_OUTPUT_PATH
        self.columns = 6
        self.filter = ['mp4']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
        return f"""<button class="filer" type="button" onclick="window.location.href='/?view=watch&_loadname={quote(f, safe='')}'">
               <img src="images/MPEG4.png" width="80">
               </button>"""


class ftDrawings(ftBase):
    def __init__(self):
        self.path = os.path.join(STORE_PATH, 'saved')
        self.columns = 3
        self.filter = ['sand']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
        pngPath = os.path.splitext(fn)[0] + '.png'
        pngUrl = '/' + pngPath.replace(os.sep, '/').lstrip('/')
        return f"""<button class="filer" type="button" onclick="window.location.href='/?view=draw&loadname={quote(p[0], safe='')}'">
             <img src="{pngUrl}">
             </button>"""

    def delete(self, f, filename):
        base, _ = os.path.splitext(filename)
        os.remove(base + '.sand')
        os.remove(base + '.png')
        return (True, 'Deleted')

    def rename(self, f, oldName, newName):
        oldBase, _ = os.path.splitext(oldName)
        path = os.path.dirname(oldName)
        newBase = os.path.join(path, newName)
        os.rename(oldBase + '.sand', newBase + '.sand')
        os.rename(oldBase + '.png', newBase + '.png')
        return (True, 'Renamed')


class ftHistory(ftDrawings):
    def __init__(self):
        self.path = os.path.join(STORE_PATH, 'history')
        self.columns = 3
        self.filter = ['sand']
        self.allowUpload = False


class ftPlaylists(ftBase):
    def __init__(self):
        self.path = os.path.join(STORE_PATH, 'playlists')
        os.makedirs(self.path, exist_ok=True)
        self.columns = 6
        self.filter = ['json']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
           return f"""<button class="filer" type="button" onclick="window.location.href='/?view=playlist&loadname={quote(p[0], safe='')}'">
               <img src="images/script.png" width="80">
               </button>"""


filetypes = {
    'Pictures':         ftPictures(),
    'Clipart':          ftClipart(),
    'Sisyphus':         ftSisyphus(),
    'Movie Scripts':    ftScripts(),
    'Movies':           ftMovies(),
    'Drawings':         ftDrawings(),
    'History':          ftHistory(),
    'Playlists':        ftPlaylists(),
}


def _render_filer_page(title, routeBase, fixedFiletype=None, rootPath=None):
    cstuff = cgistuff(title, jQuery=True)

    form = request.values
    ft = fixedFiletype or form.get('filetype', '') or 'Clipart'
    if ft not in filetypes:
        ft = fixedFiletype or 'Clipart'

    options = '\n'.join(['<option%s>%s</option>' % (' selected' if ft == name else '', name) for name in list(filetypes.keys())])

    filetype = filetypes[ft]
    basePath = rootPath or filetype.path
    path = basePath

    if 'directory' in form:
        path = form.get('directory', '') or basePath
        if len(path) and path[0] in '/.~\\':
            path = basePath

    action = form.get('action', '').lower()
    if action == 'upload':
        logging.info('Uploading')
        uploads = request.files.getlist('_file')
        allowedExts = set([ext.lower() for ext in filetype.filter])
        for fUpload in uploads:
            if fUpload is None or not fUpload.filename:
                continue
            uploadName = os.path.basename(fUpload.filename)
            name, ext = os.path.splitext(uploadName)
            extNoDot = ext[1:].lower()
            logging.info('name: %s, extension: %s' % (name, ext))
            logging.info('path: ' + path)
            if extNoDot in allowedExts and filetype.allowUpload:
                fullName = os.path.join(path, name + ext)
                logging.info('saving file to: %s' % fullName)
                if os.path.exists(fullName):
                    os.remove(fullName)
                fUpload.save(fullName)

    dirlist = os.listdir(path)
    if ft == 'History':
        # History view should be chronological; newest modified entries first.
        def _mtime(name):
            try:
                return os.path.getmtime(os.path.join(path, name))
            except OSError:
                return 0.0
        dirlist.sort(key=_mtime, reverse=True)
    else:
        dirlist.sort()

    if len(path) > len(basePath):
        dirlist.insert(0, '..')

    imgNum = 0
    columns = filetype.columns
    res = ''
    fmt = ' <button class="filer" type="submit" name="directory" value="%s"><img src="images/folder.png" width="80"><p class="filername">%s</p></button>'
    for f in dirlist:
        filename = os.path.join(path, f)
        pieces = f.split('.')
        isFile = False
        if f == '..':
            dirs = path.split('/')
            s = fmt % ('/'.join(dirs[:-1]), 'Up')
        elif f[0] in '_.':
            continue
        elif os.path.isdir(filename):
            s = fmt % (filename, pieces[0])
        elif len(pieces) != 2 or not pieces[1] in filetype.filter:
            continue
        else:
            isFile = True
            s = '%s<p class="filername">%s</p>' % (filetype.imgFunc(f, filename, pieces), pieces[0])

        res += '<tr>' if not (imgNum % columns) else ''
        button = render_actions(pieces[0], filename, ft) if isFile else ''
        res += '<td class="filer" valign="bottom" width="%d%%"><div class="filer" id="%s">%s%s</div></td>' % (int(100/columns), filename, s, button)
        imgNum += 1
        res += '</tr>' if not (imgNum % columns) else ''
    res += '</tr>' if imgNum % columns else ''

    upload = filetype.allowUpload
    ftfilter = ','.join(['.'+s for s in filetype.filter]) if upload else ""

    return ''.join([
        cstuff.headerStr(),
        cstuff.startBodyStr(),
        cstuff.navigationStr(),
        render_template(
            'filer-page.tpl',
            options=options,
            ft=ft,
            path=path,
            table=res,
            upload=upload,
            ftfilter=ftfilter,
            baseAction=routeBase,
            showFiletypeSelector=(fixedFiletype is None),
            filerTitle=(fixedFiletype or 'Filer'),
        ),
        cstuff.endBodyStr()])


def render_actions(nm, fn, ft):
    drawTargets = {
        'Pictures': ('Picture', fn),
        'Clipart': ('Clipart', fn),
        'Sisyphus': ('Sisyphus', fn),
    }
    nm = escape(nm, quote=True)
    fn = escape(fn, quote=True)
    ft = escape(ft, quote=True)
    drawButton = ''
    if ft in drawTargets:
        method, filename = drawTargets[ft]
        drawUrl = '/?view=draw&method=%s&filename=%s' % (quote(method, safe=''), quote(filename, safe=''))
        drawButton = '<button class="load" type="button" onclick="window.location.href=\'%s\'">Draw</button>' % drawUrl
    return (
        '<center class="filer-actions">'
        '%s'
        '<button class="delete" type="button" onclick="myDelete(\'%s\',\'%s\',\'%s\')">Delete</button>'
        '<button class="rename" type="button" onclick="myRename(\'%s\',\'%s\',\'%s\')">Rename</button>'
        '</center>' % (drawButton, nm, fn, ft, nm, fn, ft)
    )


@app.route('/filer', methods=['GET', 'POST'])
def filerPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='filer'))
    return _render_filer_page('Filer', '/filer')


@app.route('/clipart', methods=['GET', 'POST'])
def clipartPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='clipart'))
    return _render_filer_page('Clipart', '/clipart', fixedFiletype='Clipart')


@app.route('/thr', methods=['GET', 'POST'])
def thrPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='thr'))
    return _render_filer_page('Thr', '/thr', fixedFiletype='Sisyphus')


@app.route('/drawings', methods=['GET', 'POST'])
def drawingsPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='drawings'))
    return _render_filer_page('Drawings', '/drawings', fixedFiletype='Drawings')


@app.route('/history', methods=['GET', 'POST'])
def historyFilerPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='history'))
    return _render_filer_page('History', '/history', fixedFiletype='History')


@app.route('/filer/delete', methods=['POST'])
def filerDelete():
    # Make sure we only have safe characters in filename and nm
    filename = request.form.get('filename', '')
    ft = request.form.get('ft', '')
    if ft in filetypes:
        filetype = filetypes[ft]
        if filename.startswith(filetype.path):
            try:
                results = filetype.delete(request.form.get('nm', ''), filename)
            except OSError as error:
                results = (False, str(error))
        else:
            results = (False, 'Unexpected/incorrect path: %s' % filename)
    else:
        results = (False, 'Unexpected filetype: %s' % ft)
    return {'result': results[0], 'text': results[1]}


@app.route('/filer/rename', methods=['POST'])
def filerRename():
    # Make sure we only have safe characters in oldname, newname and nm
    oldName = request.form.get('oldname', '')
    newName = request.form.get('newname', '')
    ft = request.form.get('ft', '')
    if ft in filetypes:
        filetype = filetypes[ft]
        if oldName.startswith(filetype.path):
            try:
                results = filetype.rename(request.form.get('nm', ''), oldName, newName)
            except OSError as error:
                results = (False, str(error))
        else:
            results = (False, 'Unexpected/incorrect path: %s' % oldName)
    else:
        results = (False, 'Unexpected filetype: %s' % ft)
    return {'result': results[0], 'text': results[1]}
