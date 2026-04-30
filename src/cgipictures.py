from flask import request, redirect, url_for
from webapp import app
from cgifiler import _render_filer_page


@app.route('/pictures', methods=['GET', 'POST'])
def picturesPage():
    if request.method == 'GET' and request.args.get('embed') != '1':
        return redirect(url_for('shellPage', view='pictures'))
    return _render_filer_page('Pictures', '/pictures', fixedFiletype='Pictures')
