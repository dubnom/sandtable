#!/usr/bin/python3 -u
from bottle import route, run, static_file
import logging

from Sand import HOST_ADDR, HOST_PORT
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
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    run(host=HOST_ADDR, port=HOST_PORT, debug=True)
