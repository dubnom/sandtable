import os
import random
import copy
from html import escape
from hashlib import md5


class Params(dict):
    def __init__(self, editor=None):
        super(Params, self).__init__()
        if editor:
            for field in editor:
                self[field.name] = field.default

    def randomize(self, editor):
        for field in editor:
            # FIX: This is very specific to sandtable drawing methods
            if field.name not in ['width', 'length']:
                value = field._random()
                if value is not None:
                    self[field.name] = value

    def hash(self):
        h = md5()
        h.update(bytes(str(self.items), 'utf-8'))
        return h.hexdigest()

    def __getattribute__(self, attr):
        if attr in self:
            return self[attr]
        return super(Params, self).__getattribute__(attr)


class Dialog:
    def __init__(self, editor, form, params, autoSubmit=False):
        self.editor = editor
        self.form = form
        self.autoSubmit = autoSubmit
        self.params = params if params else Params()

    def getAction(self):
        return self.form.action

    def getMethod(self):
        return self.form.method

    def getParams(self):
        # Run through all of the editor fields converting form or editor defaults into params
        # Check all of the values for validity and generate errors if there are issues
        self.errors = {}
        for field in self.editor:
            if hasattr(self.params, field.name):
                continue
            if hasattr(field, 'fromFormRaw'):
                self.params[field.name] = field.fromFormRaw(self.form)
            elif field.name in self.form:
                try:
                    value = field.fromForm(self.form.get(field.name))
                except ValueError:
                    self.errors[field.name] = "Invalid, set to default"
                    value = field.default
                err = field.errorCheck(value)
                if err:
                    value = err[0]
                    self.errors[field.name] = err[1]
                self.params[field.name] = value
            else:
                self.params[field.name] = field.default
        return self.params

    def html(self):
        s = '<table class="form">\n'
        for field in self.editor:
            s += '<tr><td align=right><span class="form">%s</span></td>' % field.prompt
            s += '<td><span class="form">%s %s</span></td>' % (field.toForm(getattr(self.params, field.name)), field.units)
            if field.name in self.errors:
                s += '<td><span class="formError">%s</span></td>' % self.errors[field.name]
            s += '</tr>\n'
        s += '</table>'
        return s


class DialogField:
    def __init__(self, name, prompt, units, default, min, max, randRange):
        self.name = name
        self.prompt = prompt
        self.units = units
        self.default = default
        self.min = min
        self.max = max
        self.randRange = randRange

    def toForm(self, value):
        return None

    def fromForm(self, value):
        return None

    def errorCheck(self, value):
        if self.min is not None and value < self.min:
            return (self.min, "Too low, set to minimum")
        if self.max is not None and value > self.max:
            return (self.max, "Too high, set to maximum")
        return None


class DialogFloat(DialogField):
    def __init__(self, name, prompt, units='', default=0.0, min=None, max=None, randRange=None, format='%g', rbutton=False, slider=True, step=None, rRound=4):
        DialogField.__init__(self, name, prompt, units, default, min, max, randRange)
        self.format = format
        self.rbutton = rbutton
        self.slider = slider if min is not None and max is not None else False
        self.step = step if step else (max - min) / 100. if self.slider else None
        self.rRound = rRound

    def toForm(self, value):
        v = self.format % value
        if self.rbutton:
            button = '<button class="randomButton" onclick=randomFloat(%s,%g,%g)>Random</button>' % (self.name, self.min, self.max)
        else:
            button = ''
        if self.slider:
            slider = '<input name="%s_s" class="floatSlider" type="range" min="%s" max="%s" step="%s" value="%s" oninput="%s.value=%s_s.value">' % (
                self.name, self.min, self.max, self.step, v, self.name, self.name)
            sliderInform = 'onchange="%s_s.value=%s.value"' % (self.name, self.name)
        else:
            slider = ''
            sliderInform = ''
        return '<input name="%s" type="string" size="10" value="%s" %s>%s%s' % (self.name, v, sliderInform, slider, button)

    def fromForm(self, value):
        return float(value)

    def _random(self):
        if self.randRange:
            return round(random.triangular(self.randRange[0], self.randRange[1], self.default), self.rRound)
        return None if self.min is None or self.max is None else round(random.triangular(self.min, self.max, self.default), self.rRound)


class DialogFloats(DialogField):
    def __init__(self, name, prompt, units='', default=[], min=None, max=None, randRange=None, minNums=None, maxNums=None, rRound=4):
        DialogField.__init__(self, name, prompt, units, default, min, max, randRange)
        self.minNums = minNums
        self.maxNums = maxNums
        self.rRound = rRound

    def toForm(self, value):
        return '<input name="%s" type="string" size="20" value="%s">' % (self.name, self._format(value))

    def fromForm(self, value):
        return [float(num) for num in value.split(',')]

    def errorCheck(self, value):
        error = False
        for i in range(len(value)):
            if self.min is not None and value[i] < self.min:
                value[i] = self.min
                error = True
            if self.max is not None and value[i] > self.max:
                value[i] = self.max
                error = True
        if error:
            return (value, "Numbers were out of range")
        return None

    def _format(self, values):
        return ','.join(["%g" % n for n in values])

    def _random(self):
        if self.randRange:
            count = random.randint(self.minNums, self.maxNums)
            return [round(random.triangular(self.randRange[0], self.randRange[1], self.max), self.rRound) for i in range(count)]
        if self.minNums and self.maxNums:
            count = random.randint(self.minNums, self.maxNums)
            return [round(random.triangular(self.min, self.max), self.rRound) for i in range(count)]
        return None


class DialogInt(DialogField):
    def __init__(self, name, prompt, units='', default=0, min=None, max=None, randRange=None, format='%d', rbutton=False, slider=True):
        DialogField.__init__(self, name, prompt, units, default, min, max, randRange)
        self.format = format
        self.rbutton = rbutton
        self.slider = slider if min is not None and max is not None else False

    def toForm(self, value):
        v = self.format % value
        if self.rbutton:
            button = '<button class="randomButton" onclick=randomInt(%s,%d,%d)>Random</button>' % (self.name, self.min, self.max)
        else:
            button = ''
        if self.slider:
            slider = '<input name="%s_s" class="intSlider" type="range" min="%s" max="%s" value="%s" oninput="%s.value=%s_s.value">' % (
                self.name, self.min, self.max, v, self.name, self.name)
            sliderInform = 'onchange="%s_s.value=%s.value"' % (self.name, self.name)
        else:
            slider = ''
            sliderInform = ''
        return '<input name="%s" type="string" size="6" value="%s" %s>%s%s' % (self.name, v, sliderInform, slider, button)

    def fromForm(self, value):
        return int(float(value))

    def _random(self):
        if self.randRange:
            return int(random.triangular(self.randRange[0], self.randRange[1], self.default))
        return None if self.min is None or self.max is None else int(random.triangular(self.min, self.max, self.default))


class DialogInts(DialogField):
    def __init__(self, name, prompt, units='', default=[], min=None, max=None, randRange=None, minNums=None, maxNums=None):
        DialogField.__init__(self, name, prompt, units, default, min, max, randRange)
        self.minNums = minNums
        self.maxNums = maxNums

    def toForm(self, value):
        return '<input name="%s" type="string" size="20" value="%s">' % (self.name, self._format(value))

    def fromForm(self, value):
        return [int(num) for num in value.split(',')]

    def errorCheck(self, value):
        error = False
        for i in range(len(value)):
            if self.min is not None and value[i] < self.min:
                value[i] = self.min
                error = True
            if self.max is not None and value[i] > self.max:
                value[i] = self.max
                error = True
        if error:
            return (value, "Numbers were out of range")
        return None

    def _format(self, values):
        return ','.join(["%d" % n for n in values])

    def _random(self):
        if self.randRange:
            return [random.randint(self.randRange[0], self.randRange[1]) for i in range(random.randint(self.minNums, self.maxNums))]
        if self.minNums and self.maxNums:
            return [random.randint(self.min, self.max) for i in range(random.randint(self.minNums, self.maxNums))]
        return None


class DialogStr(DialogField):
    def __init__(self, name, prompt, units='', default='', length=20):
        DialogField.__init__(self, name, prompt, units, default, None, None, None)
        self.length = length

    def toForm(self, value):
        return '<input name="%s" type="string" size="%d" value="%s">' % (self.name, self.length, escape(value))

    def fromForm(self, value):
        return value

    def _random(self):
        return None


class DialogList(DialogField):
    def __init__(self, name, prompt, units='', default='', list=[]):
        DialogField.__init__(self, name, prompt, units, default, None, None, None)
        self.list = list

    def toForm(self, value):
        str = '<select name="%s">' % (self.name)
        for item in self.list:
            selected = ' selected' if item == value else ''
            str += '<option%s>%s</option>' % (selected, item)
        str += '</select>'
        return str

    def fromForm(self, value):
        return value

    def _random(self):
        return self.list[random.randint(0, len(self.list) - 1)]


class Dialog2Choices(DialogList):
    def __init__(self, name, prompt, units='', default=False, list=['True', 'False']):
        DialogList.__init__(self, name, prompt, units, default, list)

    def toForm(self, value):
        if value:
            return DialogList.toForm(self, self.list[1])
        else:
            return DialogList.toForm(self, self.list[0])

    def fromForm(self, value):
        return value == self.list[1]

    def _random(self):
        return random.randint(0, 1)


class DialogYesNo(Dialog2Choices):
    def __init__(self, name, prompt, units='', default=False):
        DialogList.__init__(self, name, prompt, units, default, list=['No', 'Yes'])


class DialogTrueFalse(Dialog2Choices):
    def __init__(self, name, prompt, units='', default=False):
        DialogList.__init__(self, name, prompt, units, default, list=['False', 'True'])


class DialogOnOff(Dialog2Choices):
    def __init__(self, name, prompt, units='', default=False):
        DialogList.__init__(self, name, prompt, units, default, list=['Off', 'On'])


class DialogFile(DialogField):
    def __init__(self, name, prompt, default='', filter='', extensions=False):
        DialogField.__init__(self, name, prompt, '', default, None, None, None)
        self.filter = filter
        self.filters = filter.split('|')
        self.extensions = extensions

    def _extension(self, filename):
        pieces = filename.split('.')
        if len(pieces) < 2:
            return ''
        return '.' + pieces[-1].lower()

    def toForm(self, value):
        str = '<select name="%s" onChange="form.submit()">\n' % (self.name)
        if value.endswith('/'):
            value = value[0:len(value)-1]
        if os.path.isdir(value):
            path = value
        else:
            path, value = os.path.split(value)
        # FIX: Check for path violations
        up, nada = os.path.split(path)
        if up and len(up):
            str += '<option value="%s">[Up a level]</option>\n' % up
        else:
            str += '<option value="">Chose a file</option>\n'
        dirlist = os.listdir(path)
        dirlist.sort()
        for f in dirlist:
            filename = os.path.join(path, f)
            if f.startswith('.'):
                continue
            elif os.path.isdir(filename):
                show = f + '...'
            elif self._extension(f) in self.filters:
                if self.extensions:
                    show = f[:-len(self._extension(f))]
                else:
                    show = f
            else:
                continue
            if f == value:
                selected = ' selected'
            else:
                selected = ''
            str += '<option value="%s"%s>%s</option>\n' % (filename, selected, show)
        str += '</select>'
        return str

    def fromForm(self, value):
        if value and len(value) and not value[0] in '/\\~.':
            return value
        return self.default

    def _random(self):
        path = self.default
        def fl(f): return not f.startswith('.') and (self._extension(f) in self.filters or os.path.isdir(os.path.join(path, f)))
        while True:
            dirlist = list(filter(fl, os.listdir(path)))
            if not len(dirlist):
                return None
            f = dirlist[random.randint(0, len(dirlist) - 1)]
            if not os.path.isdir(os.path.join(path, f)):
                return os.path.join(path, f)
            path = os.path.join(path, f)


class DialogFont(DialogField):
    def __init__(self, name, prompt, default='', filter='', extensions=False):
        DialogField.__init__(self, name, prompt, '', default, None, None, None)
        self.filter = filter
        self.filters = filter.split('|')
        self.extensions = extensions

    def _extension(self, filename):
        pieces = filename.split('.')
        if len(pieces) < 2:
            return ''
        return '.' + pieces[-1].lower()

    def toForm(self, value):
        str = '<select name="%s">\n' % self.name
        fonts = self._getFonts()
        for font in fonts:
            selected = ' selected' if font[1] == value else ''
            str += '<option value="%s"%s>%s</option>\n' % (font[1], selected, font[0])
        str += '</select>'
        return str

    def _getFonts(self):
        fonts = []
        for root, dirs, files in os.walk('/usr/share/fonts'):
            for file in files:
                if file.endswith('.ttf'):
                    fonts.append((file[:-4], os.path.join(root, file)))
        fonts.sort()
        return fonts

    def fromForm(self, value):
        return value

    def _random(self):
        fonts = self._getFonts()
        return fonts[random.randint(0, len(fonts) - 1)][1]


class DialogMulti(DialogField):
    def __init__(self, name, prompt, default='', rows=5, cols=20):
        DialogField.__init__(self, name, prompt, '', default, None, None, None)
        self.rows = rows
        self.cols = cols

    def toForm(self, value):
        str = '<textarea name="%s" rows="%d" cols="%d">' % (self.name, self.rows, self.cols)
        str += escape(value)
        str += '</textarea>'
        return str

    def fromForm(self, value):
        return value

    def _random(self):
        return None


class DialogColor(DialogField):
    def __init__(self, name, prompt, default=(255, 255, 255)):
        DialogField.__init__(self, name, prompt, '', default, None, None, None)

    def toForm(self, value):
        color = "#%02x%02x%02x" % value
        str = '<input name="%s" type="color" value="%s">' % (self.name, color)
        return str

    def fromForm(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i+int(lv/3)], 16) for i in range(0, lv, int(lv/3)))

    def _random(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


class DialogBreak(DialogField):
    def __init__(self, name='', prompt='', default=''):
        DialogField.__init__(self, name, prompt, '', default, None, None, None)

    def toForm(self, value):
        return '<hr>'

    def fromForm(self, value):
        pass

    def _random(self):
        return None


class ArrayValue:
    def __repr__(self):
        return '['+','.join(['%s:%s' % (n, getattr(self, n)) for n in [x for x in dir(self) if not x.startswith('_')]])+']'


class DialogArray(DialogField):
    def __init__(self, name='', prompt='', default='', fields=None, length=3):
        DialogField.__init__(self, name, prompt, '', default, None, None, None)
        self.fields = fields
        self.length = length

    def toForm(self, value):
        result = '<table>'

        titles = '<tr>'
        units = '<tr>'
        for field in self.fields:
            titles += '<th>%s</th>' % field.prompt
            units += '<th>%s</th>' % field.units
        titles += '</tr>'
        units += '</tr>'
        result += titles + units

        for row in range(self.length):
            result += '<tr>'
            for field in self.fields:
                fieldCopy = copy.copy(field)
                fieldCopy.name += "-%d" % row
                result += '<td><span class="form">%s</span></td>' % fieldCopy.toForm(getattr(value[row], field.name))
            result += '</tr>'

        result += '</table>'
        return result

    def fromFormRaw(self, form):
        value = []
        for row in range(self.length):
            av = ArrayValue()
            for field in self.fields:
                fieldName = '%s-%d' % (field.name, row)
                if fieldName in form:
                    try:
                        v = field.fromForm(form.get(fieldName))
                    except ValueError:
                        v = field.default
                    err = field.errorCheck(v)
                    if err:
                        v = err[0]
                        # FIX: Finish error display
                    setattr(av, field.name, v)
                else:
                    setattr(av, field.name, field.default)
            value.append(av)
        return value
