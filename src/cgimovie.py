from flask import request, render_template, redirect, url_for
import os
import subprocess

from Sand import MOVIE_SCRIPT_PATH, ROOT_DIRECTORY, MOVIE_STATUS_LOG
from webapp import app
from cgistuff import cgistuff


@app.route('/movie', methods=['GET', 'POST'])
def moviePage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        redirectArgs = {'view': 'movie'}
        for key, value in request.args.items():
            if key in ('embed', 'view'):
                continue
            redirectArgs[key] = value
        return redirect(url_for('shellPage', **redirectArgs))

    # Handle form operations
    form = request.values
    action = form.get('action', '').lower()
    loadname = form.get('loadname', '').strip()
    name = form.get('_name', '')
    if not action and loadname:
        action = 'load'
        name = loadname

    script = '<Movie>\n</Movie>'
    if action == 'load':
        name = form.get('_loadname', '') or loadname
        try:
            with open('%s%s.xml' % (MOVIE_SCRIPT_PATH, name)) as f:
                script = f.read()
        except Exception as e:
            script = "Couldn't load '%s'\n%s" % (name, e)

    if action in ('save', 'preview', 'sand'):
        script = form.get('script', script)
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
    return ''.join([
        cstuff.standardTopStr(),
        render_template('movie-page.tpl', filenames='\n'.join(scripts), script=script, name=name),
        cstuff.endBodyStr()])
