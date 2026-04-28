#!/usr/bin/python3 -u
import logging
import os
from flask import send_from_directory

import Sand
from Sand import HOST_ADDR, HOST_PORT
from webapp import PROJECT_ROOT, app
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


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


@app.route('/images/<path:filename>')
def images_static(filename):
    # Cache image assets to avoid repeated conditional GETs for draw button thumbnails.
    return send_from_directory(str(PROJECT_ROOT / 'images'), filename, max_age=86400)


@app.route('/data/<path:filename>')
def data_static(filename):
    return send_from_directory(str(PROJECT_ROOT / 'data'), filename)


@app.route('/store/<path:filename>')
def store_static(filename):
    return send_from_directory(str(PROJECT_ROOT / 'store'), filename)


@app.route('/pictures/<path:filename>')
def pictures_static(filename):
    return send_from_directory(str(PROJECT_ROOT / 'pictures'), filename)


@app.route('/movies/<path:filename>')
def movies_static(filename):
    return send_from_directory(str(PROJECT_ROOT / 'movies'), filename)


@app.route('/scripts/<path:filename>')
def scripts_static(filename):
    return send_from_directory(str(PROJECT_ROOT / 'scripts'), filename)


@app.route('/favicon.ico')
def favicon_static():
    return send_from_directory(str(PROJECT_ROOT / 'images'), 'favicon.ico')


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    adhoc_ssl_default = bool(getattr(Sand, 'ADHOC_SSL', False))
    adhoc_ssl = _env_flag('SANDTABLE_ADHOC_SSL', adhoc_ssl_default)
    debug_default = bool(getattr(Sand, 'SERVER_DEBUG', False))
    debug_mode = _env_flag('SANDTABLE_DEBUG', debug_default)
    ssl_context = 'adhoc' if adhoc_ssl else None
    app.run(
        host=HOST_ADDR,
        port=HOST_PORT,
        debug=debug_mode,
        use_reloader=debug_mode,
        threaded=True,
        ssl_context=ssl_context,
    )
