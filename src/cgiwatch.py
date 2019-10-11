from bottle import request, route, post, get, template
import os

from Sand import *
from cgistuff import *


@route('/watch')
@post('/watch')
def watchPage():
    cstuff = cgistuff( 'Watch Movies' )
    
    fileNames = sorted( filter( lambda n: n.endswith('.mp4'), os.listdir( MOVIE_OUTPUT_PATH )))
    form = request.forms

    return [
        cstuff.standardTopStr(),
        template( 'watch-page', fileNames=fileNames, path=MOVIE_OUTPUT_PATH, loadname=form._loadname, width=MOVIE_WIDTH, height=MOVIE_HEIGHT ),
        cstuff.endBodyStr() ]
