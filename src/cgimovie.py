from bottle import request, route, post, get, template
import os
import subprocess

from Sand import MOVIE_SCRIPT_PATH, ROOT_DIRECTORY, MOVIE_STATUS_LOG
from cgistuff import cgistuff


@route('/movie')
@post('/movie')
@get('/movie')
def moviePage():
    # Handle form operations
    form = request.forms
    action = form.action.lower() if form.action else ''
    name = form._name

    script = '<Movie>\n</Movie>'
    if action == 'load':
        name = form._loadname
        try:
            with open('%s%s.xml' % (MOVIE_SCRIPT_PATH, name)) as f:
                script = f.read()
        except Exception as e:
            script = "Couldn't load '%s'\n%s" % (name, e)

    if action in ('save', 'preview', 'sand'):
        script = form.script
        with open('%s%s.xml' % (MOVIE_SCRIPT_PATH, name), 'wt') as f:
            f.write(script)
        flags = '--sand' if action == 'sand' else ''
        subprocess.Popen('./src/Movie.py %s %s >%s 2>&1' % (name, flags, MOVIE_STATUS_LOG), shell=True, cwd=ROOT_DIRECTORY)

    scripts = []
    fileNames = os.listdir(MOVIE_SCRIPT_PATH)
    fileNames.sort()
    for fileName in fileNames:
        if fileName.endswith('.xml'):
            sname = fileName[:-4]
            scripts.append('<option value=%s>%s</option>' % (sname, sname))

    cstuff = cgistuff('Make Movies')
    return [
        cstuff.standardTopStr(),
        template('movie-page', filenames='\n'.join(scripts), script=script, name=name),
        cstuff.endBodyStr()]
