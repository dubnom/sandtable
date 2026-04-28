from flask import render_template, request

from webapp import app
from cgistuff import getInlineCss, menuItems


@app.route('/', methods=['GET'])
def shellPage():
    allowed = {path for _, path in menuItems}
    initialView = str(request.args.get('view', 'draw')).strip().lstrip('/')
    if initialView not in allowed:
        initialView = 'draw'
    return render_template('shell-page.tpl', inline_css=getInlineCss(), menuItems=menuItems, initialView=initialView)
