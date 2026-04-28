from flask import request, render_template
import os

from Sand import MOVIE_OUTPUT_PATH, MOVIE_WIDTH, MOVIE_HEIGHT
from webapp import app
from cgistuff import cgistuff


@app.route('/watch', methods=['GET', 'POST'])
def watchPage():
    cstuff = cgistuff('Watch Movies')

    fileNames = sorted([n for n in os.listdir(MOVIE_OUTPUT_PATH) if n.endswith('.mp4')])
    loadname = request.values.get('_loadname', '')
    selected_index = fileNames.index(loadname) + 1 if loadname in fileNames else 0

    return ''.join([
        cstuff.standardTopStr(),
        render_template('watch-page.tpl', fileNames=fileNames, path=MOVIE_OUTPUT_PATH, loadname=loadname, selected_index=selected_index, width=MOVIE_WIDTH, height=MOVIE_HEIGHT),
        cstuff.endBodyStr()])
