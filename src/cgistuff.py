from flask import render_template, request
from pathlib import Path

menuItems = (
    ('Draw', 'draw'),
    ('History', 'history'),
    ('Playlist', 'playlist'),
    ('Lights', 'lights'),
    ('Pictures', 'pictures'),
    ('Watch Movie', 'watch'),
    ('Make Movie', 'movie'),
    ('Filer', 'filer'),
    ('Admin', 'admin'),
)

_CSS_PATH = Path(__file__).resolve().parent.parent / 'sandtable.css'
try:
    _INLINE_CSS = _CSS_PATH.read_text(encoding='utf-8')
except OSError:
    _INLINE_CSS = ''


def getInlineCss():
    return _INLINE_CSS


class cgistuff:
    def __init__(self, title, jQuery=False, jQueryUI=False):
        self.title = title
        self.jQuery = jQuery
        self.jQueryUI = jQueryUI

    def headerStr(self, meta=''):
        if request.args.get('embed') == '1':
            return ''
        return render_template('header.tpl', jQuery=self.jQuery, jQueryUI=self.jQueryUI, meta=meta, title=self.title, inline_css=_INLINE_CSS)

    def startBodyStr(self):
        if request.args.get('embed') == '1':
            return ''
        return '<body><div class="pageTitle"><span class="title">Sand Table - %s</span><br></div>' % self.title

    def navigationStr(self):
        if request.args.get('embed') == '1':
            return ''
        return '<div class="navigation">' + ' | '.join(['<a href="/?view=%s">%s</a>' % (item[1], item[0]) for item in menuItems]) + '</div>'

    def standardTopStr(self):
        return self.headerStr() + self.startBodyStr() + self.navigationStr()

    def endBodyStr(self):
        if request.args.get('embed') == '1':
            return ''
        return render_template('statusbar.tpl') + render_template('footer.tpl', jQuery=self.jQuery)
