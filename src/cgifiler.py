from bottle import request, route, get, post, template, SimpleTemplate
import os
import logging
from Sand import PICTURE_PATH, CLIPART_PATH, THR_PATH, MOVIE_SCRIPT_PATH, STORE_PATH, MOVIE_OUTPUT_PATH
from cgistuff import cgistuff


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
        return """<button type="button" class="filer" onclick='mySubmit("draw", "method","Picture", "filename","%s")'>
               <img src="%s" width="80" align="center">
               </button>""" % (fn, fn)


class ftClipart(ftBase):
    def __init__(self):
        self.path = CLIPART_PATH
        self.columns = 6
        self.filter = ['dxf']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        return """<button type="button" class="filer" onclick='mySubmit("draw", "method","Clipart", "filename","%s")'>
               <img src="images/DXF.png" width="80">
               </button>""" % fn

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
        return """<button type="button" class="filer" onclick='mySubmit("draw", "method","Sisyphus", "filename","%s")'>
               <img src="images/thr.png" width="80">
               </button>""" % fn

class ftScripts(ftBase):
    def __init__(self):
        self.path = MOVIE_SCRIPT_PATH
        self.columns = 6
        self.filter = ['xml']
        self.allowUpload = True

    def imgFunc(self, f, fn, p):
        return """<button type="button" class="filer" onclick='mySubmit("movie", "action","load", "_loadname","%s")'>
               <img src="images/script.png" width="80">
               </button>""" % p[0]


class ftMovies(ftBase):
    def __init__(self):
        self.path = MOVIE_OUTPUT_PATH
        self.columns = 6
        self.filter = ['mp4']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
        return """<button type="button" class="filer" onclick='mySubmit("watch", "action","load", "_loadname","%s")'>
               <img src="images/MPEG4.png" width="80">
               </button>""" % f


class ftDrawings(ftBase):
    def __init__(self):
        self.path = STORE_PATH
        self.columns = 3
        self.filter = ['sand']
        self.allowUpload = False

    def imgFunc(self, f, fn, p):
        return """<button type="button" class="filer" onclick='mySubmit("draw", "action","load", "_loadname","%s")'>
               <img src="%s%s.png">
               </button>""" % (p[0], self.path, p[0])

    def delete(self, f, filename):
        os.remove(os.path.join(self.path, f + '.sand'))
        os.remove(os.path.join(self.path, f + '.png'))
        return (True, 'Deleted')

    def rename(self, f, oldName, newName):
        os.rename(os.path.join(self.path, f + '.sand'), os.path.join(self.path, newName + '.sand'))
        os.rename(os.path.join(self.path, f + '.png'),  os.path.join(self.path, newName + '.png'))
        return (True, 'Renamed')


filetypes = {
    'Pictures':         ftPictures(),
    'Clipart':          ftClipart(),
    'Sisyphus':         ftSisyphus(),
    'Movie Scripts':    ftScripts(),
    'Movies':           ftMovies(),
    'Saved Drawings':   ftDrawings(),
}


nj = SimpleTemplate("""
<center>
 <button class="delete" type="button" onclick="myDelete('{{nm}}','{{fn}}','{{ft}}')">Delete</button>
 <button class="rename" type="button" onclick="myRename('{{nm}}','{{fn}}','{{ft}}')">Rename</button>
</center>""")


@route('/filer')
@post('/filer')
@get('/filer')
def filerPage():
    cstuff = cgistuff('Filer', jQuery='True')

    form = request.forms
    ft = form.filetype or 'Saved Drawings'

    options = '\n'.join(['<option%s>%s</option>' % (' selected' if ft == name else '', name) for name in list(filetypes.keys())])

    filetype = filetypes[ft]
    path = filetype.path

    if 'directory' in form:
        path = form.directory or filetype.path
        if len(path) and path[0] in '/.~\\':
            path = filetype.path

    # Check for uploads
    action = form.action.lower() if form.action else ''
    if action == 'upload':
        logging.info('Uploading')
        fUpload = request.files.get('_file')
        name, ext = os.path.splitext(fUpload.filename)
        logging.info('name: %s, extension: %s' % (name, ext))
        logging.info('path: ' + path)
        if ext[1:] in filetype.filter and filetype.allowUpload:
            fullName = os.path.join(path, name + ext)
            logging.info('saving picture to: %s' % fullName)
            fUpload.save(fullName, overwrite=True)

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
            s = '%s<p class="filername">%s</p>' % (filetype.imgFunc(f, filename, pieces), pieces[0])

        res += '<tr>' if not (imgNum % columns) else ''
        button = nj.render(nm=pieces[0], fn=filename, ft=ft)
        res += '<td class="filer" valign="bottom" width="%d%%"><div class="filer" id="%s">%s%s</div></td>' % (int(100/columns), filename, s, button)
        imgNum += 1
        res += '</tr>' if not (imgNum % columns) else ''
    res += '</tr>' if imgNum % columns else ''

    upload = filetype.allowUpload
    ftfilter = ','.join(['.'+s for s in filetype.filter]) if upload else ""

    return [
        cstuff.headerStr(),
        cstuff.startBodyStr(),
        cstuff.navigationStr(),
        template('filer-page', options=options, ft=ft, path=path, table=res, upload=upload, ftfilter=ftfilter),
        cstuff.endBodyStr()]


@post('/filer/delete')
def filerDelete():
    # Make sure we only have safe characters in filename and nm
    filename = request.forms.filename
    ft = request.forms.ft
    if ft in filetypes:
        filetype = filetypes[ft]
        if filename.startswith(filetype.path):
            try:
                results = filetype.delete(request.forms.nm, filename)
            except OSError as error:
                results = (False, str(error))
        else:
            results = (False, 'Unexpected/incorrect path: %s' % filename)
    else:
        results = (False, 'Unexpected filetype: %s' % ft)
    return {'result': results[0], 'text': results[1]}


@post('/filer/rename')
def filerRename():
    # Make sure we only have safe characters in oldname, newname and nm
    oldName = request.forms.oldname
    newName = request.forms.newname
    ft = request.forms.ft
    if ft in filetypes:
        filetype = filetypes[ft]
        if oldName.startswith(filetype.path):
            try:
                results = filetype.rename(request.forms.nm, oldName, newName)
            except OSError as error:
                results = (False, str(error))
        else:
            results = (False, 'Unexpected/incorrect path: %s' % oldName)
    else:
        results = (False, 'Unexpected filetype: %s' % ft)
    return {'result': results[0], 'text': results[1]}
