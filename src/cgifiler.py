from flask import request, render_template, redirect, url_for
import os
import logging
from html import escape
from urllib.parse import quote
from Sand import PICTURE_PATH, CLIPART_PATH, THR_PATH, MOVIE_SCRIPT_PATH, STORE_PATH, MOVIE_OUTPUT_PATH
from webapp import app
from cgistuff import cgistuff
from history import History


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
        self.filter = ['png', 'jpg', 'gif']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        return """<a class="filer" href="/?view=draw&method=Picture&filename=%s">
             <img src="%s" width="80" align="center">
             </a>""" % (quote(fn, safe=''), fn)


class ftClipart(ftBase):
    def __init__(self):
        self.path = CLIPART_PATH
        self.columns = 6
        self.filter = ['svg']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        return """<a class="filer" href="/?view=draw&method=Clipart&filename=%s">
             <img src="images/DXF.png" width="80">
             </a>""" % quote(fn, safe='')

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
        return """<a class="filer" href="/?view=draw&method=Sisyphus&filename=%s">
             <img src="images/thr.png" width="80">
             </a>""" % quote(fn, safe='')

class ftScripts(ftBase):
    def __init__(self):
        self.path = MOVIE_SCRIPT_PATH
        self.columns = 6
        self.filter = ['xml']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        return """<a class="filer" href="/?view=movie&loadname=%s">
             <img src="images/script.png" width="80">
             </a>""" % quote(p[0], safe='')


class ftMovies(ftBase):
    def __init__(self):
        self.path = MOVIE_OUTPUT_PATH
        self.columns = 6
        self.filter = ['mp4']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
        return """<a class="filer" href="/?view=watch&_loadname=%s">
             <img src="images/MPEG4.png" width="80">
             </a>""" % quote(f, safe='')


class ftDrawings(ftBase):
    def __init__(self):
        self.path = STORE_PATH
        self.columns = 3
        self.filter = ['sand']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
        pngPath = os.path.splitext(fn)[0] + '.png'
        pngUrl = '/' + pngPath.replace(os.sep, '/').lstrip('/')
        return """<a class="filer" href="/?view=draw&loadname=%s">
               <img src="%s">
               </a>""" % (p[0], pngUrl)

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


filetypes = {
    'Pictures':         ftPictures(),
    'Clipart':          ftClipart(),
    'Sisyphus':         ftSisyphus(),
    'Movie Scripts':    ftScripts(),
    'Movies':           ftMovies(),
    'Saved Drawings':   ftDrawings(),
}


def render_actions(nm, fn, ft):
    nm = escape(nm, quote=True)
    fn = escape(fn, quote=True)
    ft = escape(ft, quote=True)
    return (
        '<center>'
        '<button class="delete" type="button" onclick="myDelete(\'%s\',\'%s\',\'%s\')">Delete</button>'
        '<button class="rename" type="button" onclick="myRename(\'%s\',\'%s\',\'%s\')">Rename</button>'
        '</center>' % (nm, fn, ft, nm, fn, ft)
    )


@app.route('/filer', methods=['GET', 'POST'])
def filerPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='filer'))

    cstuff = cgistuff('Filer', jQuery=True)

    form = request.values
    ft = form.get('filetype', '') or 'Saved Drawings'

    options = '\n'.join(['<option%s>%s</option>' % (' selected' if ft == name else '', name) for name in list(filetypes.keys())])

    filetype = filetypes[ft]
    path = filetype.path

    if 'directory' in form:
        path = form.get('directory', '') or filetype.path
        if len(path) and path[0] in '/.~\\':
            path = filetype.path

    # Check for uploads
    action = form.get('action', '').lower()
    if action == 'upload':
        logging.info('Uploading')
        fUpload = request.files.get('_file')
        if fUpload is not None:
            name, ext = os.path.splitext(fUpload.filename)
            logging.info('name: %s, extension: %s' % (name, ext))
            logging.info('path: ' + path)
            if ext[1:] in filetype.filter and filetype.allowUpload:
                fullName = os.path.join(path, name + ext)
                logging.info('saving picture to: %s' % fullName)
                if os.path.exists(fullName):
                    os.remove(fullName)
                fUpload.save(fullName)

    # Query and display the contents of the directory
    dirlist = os.listdir(path)
    dirlist.sort()

    if len(path) > len(filetype.path):
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
        render_template('filer-page.tpl', options=options, ft=ft, path=path, table=res, upload=upload, ftfilter=ftfilter,
                        store_root=STORE_PATH, saved_directory=os.path.join(STORE_PATH, 'saved')),
        cstuff.endBodyStr()])


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
