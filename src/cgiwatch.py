from bottle import request, route, post, get, template
import os

from Sand import *
from cgistuff import *


@route('/watch')
@post('/watch')
def watchPage():
    cstuff = cgistuff( 'Watch Movies' )
    
    fileNames = sorted( [n for n in os.listdir( MOVIE_OUTPUT_PATH ) if n.endswith('.mp4')])
    form = request.forms

    return [
        cstuff.standardTopStr(),
        template( 'watch-page', fileNames=fileNames, path=MOVIE_OUTPUT_PATH, loadname=form._loadname, width=MOVIE_WIDTH, height=MOVIE_HEIGHT ),
        cstuff.endBodyStr() ]
