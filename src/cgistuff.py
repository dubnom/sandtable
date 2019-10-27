from bottle import template, SimpleTemplate

menuItems = (
    ('Draw', 'draw'),
    ('History', 'history'),
    ('Lights', 'lights'),
    ('Pictures', 'pictures'),
    ('Watch Movie', 'watch'),
    ('Make Movie', 'movie'),
    ('Filer', 'filer'),
    ('Admin', 'admin'),
)


startBodyTemplate = SimpleTemplate("""<body><span class="title">Sand Table - {{title}}</span><br>""")


class cgistuff:
    def __init__(self, title, jQuery=False, jQueryUI=False):
        self.title = title
        self.jQuery = jQuery
        self.jQueryUI = jQueryUI

    def headerStr(self, meta=''):
        return template('header', jQuery=self.jQuery, jQueryUI=self.jQueryUI, meta=meta, title=self.title)

    def startBodyStr(self):
        return startBodyTemplate.render(title=self.title)

    def navigationStr(self):
        return '<div class="navigation">' + ' | '.join(['<a href="%s">%s</a>' % (item[1], item[0]) for item in menuItems]) + '</div>'

    def standardTopStr(self):
        return self.headerStr() + self.startBodyStr() + self.navigationStr()

    def endBodyStr(self):
        return template('footer', jQuery=self.jQuery)
