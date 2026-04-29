#!/usr/bin/python3 -u
import logging
import os
from flask import send_from_directory

import Sand
from Sand import HOST_ADDR, HOST_PORT
from webapp import PROJECT_ROOT, app, socketio
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
import cgiplaylist
import cgistatus
import cgishell


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


_IMMUTABLE_IMAGE_MAX_AGE = 31536000
_IMAGE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif', '.bmp', '.ico'
}


def _send_static_asset(directory, filename):
    ext = os.path.splitext(str(filename).lower())[1]
    if ext in _IMAGE_EXTENSIONS:
        response = send_from_directory(str(directory), filename, max_age=_IMMUTABLE_IMAGE_MAX_AGE)
        response.cache_control.public = True
        response.cache_control.immutable = True
        return response
    return send_from_directory(str(directory), filename)


@app.route('/images/<path:filename>')
def images_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'images', filename)


@app.route('/data/<path:filename>')
def data_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'data', filename)


@app.route('/store/<path:filename>')
def store_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'store', filename)


@app.route('/pictures/<path:filename>')
def pictures_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'pictures', filename)


@app.route('/clipart/<path:filename>')
def clipart_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'clipart', filename)


@app.route('/movies/<path:filename>')
def movies_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'movies', filename)


@app.route('/scripts/<path:filename>')
def scripts_static(filename):
    return _send_static_asset(PROJECT_ROOT / 'scripts', filename)


@app.route('/favicon.ico')
def favicon_static():
    return _send_static_asset(PROJECT_ROOT / 'images', 'favicon.ico')


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    adhoc_ssl_default = bool(getattr(Sand, 'ADHOC_SSL', False))
    adhoc_ssl = _env_flag('SANDTABLE_ADHOC_SSL', adhoc_ssl_default)
    debug_default = bool(getattr(Sand, 'SERVER_DEBUG', False))
    debug_mode = _env_flag('SANDTABLE_DEBUG', debug_default)
    ssl_context = 'adhoc' if adhoc_ssl else None
    run_kwargs = {
        'host': HOST_ADDR,
        'port': HOST_PORT,
        'debug': debug_mode,
        'use_reloader': debug_mode,
        'ssl_context': ssl_context,
    }
    # Newer Flask-SocketIO requires this flag when using Werkzeug directly.
    try:
        socketio.run(app, allow_unsafe_werkzeug=True, **run_kwargs)
    except TypeError:
        socketio.run(app, **run_kwargs)
