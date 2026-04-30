from flask import request, redirect, url_for
from webapp import app


@app.route('/drawing-history', methods=['GET', 'POST'])
def historyPage():
    return redirect(url_for('historyFilerPage', **request.args))
