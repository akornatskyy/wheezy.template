
"""
"""

import getopt
import sys

from wheezy.template.engine import Engine
from wheezy.template.ext.code import CodeExtension
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader

try:
    import json
except ImportError:  # pragma: nocover
    try:
        import simplejson as json
    except ImportError:  # pragma: nocover
        json = None

try:
    from wheezy.html.utils import escape_html as escape
except ImportError:  # pragma: nocover
    try:
        from html import escape
    except ImportError:  # pragma: nocover
        from cgi import escape


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def main(args=None):
    if not json:  # pragma: nocover
        print('error: json module is not available')
        return 1
    args = parse_args(args or sys.argv[1:])
    if not args:
        return 2
    ts = args.token_start
    extensions = [CoreExtension(ts), CodeExtension(ts)]
    extensions.extend(args.extensions)
    engine = Engine(FileLoader(args.searchpath), extensions)
    engine.global_vars.update({'h': escape})
    t = engine.get_template(args.template)
    sys.stdout.write(t.render(load_context(args.context)))
    return 0


def load_context(sources):
    c = {}
    for s in sources:
        if s.endswith('.json'):
            s = json.load(open(s))
        else:
            s = json.loads(s)
        c.update(s)
    return c


def parse_args(args):
    try:
        opts, value = getopt.getopt(args, 's:t:wh')
    except getopt.GetoptError:
        e = sys.exc_info()[1]
        usage()
        print('error: %s' % e)
        return
    args = AttrDict(token_start='@', searchpath=['.'], extensions=[])
    for o, a in opts:
        if o == '-h':
            return
        elif o == '-t':
            args.token_start = a
        elif o == '-s':
            args.searchpath = a.split(';')
        elif o == '-w':  # pragma: nocover
            from wheezy.html.ext.template import WhitespaceExtension
            args.extensions.append(WhitespaceExtension())
    if not value:
        usage()
        return
    args.template = value[0]
    args.context = value[1:]
    return args


def usage():
    from wheezy.template import __version__
    print("""\
wheezy.template %s
Copyright (C) 2012-2015 by Andriy Kornatskyy

renders a template with the given context.

usage: %s template [ context ... ]

positional arguments:

  template    a filename
  context     a filename or JSON string

optional arguments:

  -s path     search path for templates ( . )
  -t token    token start ( @ )
  -w          whitespace clean up
  -h          show this help message
""" % (__version__, sys.argv[0]))


if __name__ == '__main__':  # pragma: nocover
    sys.exit(main())
