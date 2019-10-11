#!/usr/bin/python
from bottle import route, default_app, run, static_file
import socket

from Sand import *
import cgidraw
import cgihistory
import cgilights
import cgipictures
import cgiwatch
import cgimovie
import cgihelp
import cgiadmin
import cgifiler
import cgidhelp

@route('/images/<filename>')
def server_static(filename):
    return static_file(filename, root='images')

@route('/data/<filename>')
def server_static(filename):
    return static_file(filename, root='data')

@route('/store/<filename>')
def server_static(filename):
    return static_file(filename, root='store')

@route('/pictures/<filename>')
def server_static(filename):
    return static_file(filename, root='pictures')

@route('/movies/<filename>')
def server_static(filename):
    return static_file(filename, root='movies')

@route('/scripts/<filename>')
def server_static(filename):
    return static_file(filename, root='scripts')


@route('/sandtable.css')
def server_static():
    return static_file('sandtable.css', root='')

@route('/favicon.ico')
def server_static():
    return static_file('favicon.ico', root='images')


if __name__ == "__main__":
    run(host='0.0.0.0',port=80,debug=True)
    #run(host=socket.gethostbyname(socket.gethostname()),port=80,debug=True)
else:
    application = default_app()
    from past.exceptions.errormiddleware import ErrorMiddleware
    application = ErrorMiddleware(application, debug=True)

