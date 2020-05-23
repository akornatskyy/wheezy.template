""" Custom HTML escape by default extension.
"""

import unittest

from wheezy.template.comp import PY3
from wheezy.template.engine import Engine
from wheezy.template.loader import DictLoader
from wheezy.template.ext.core import CoreExtension

try:
    from wheezy.html.utils import escape_html as escape
except ImportError:
    try:
        from html import escape
    except ImportError:
        from cgi import escape


s = PY3 and 'str' or 'unicode'


def build_var(builder, lineno, token, value):
    assert token == 'var'
    var, var_filters = value
    if not var_filters:
        builder.add(lineno, 'w(e(' + s + '(' + var + ')))')
        return True
    if 'safe' in var_filters:
        builder.add(lineno, 'w(' + var + ')')
        return True
    return False


class EscapeExtension(object):
    builder_rules = [
        ('var', build_var)
    ]


# setup
template = """
@require(var)
@def x(s):
  <meta name="@s" />
@end
@var @var!e @var!s @x(var)!safe
"""

engine = Engine(
    loader=DictLoader({
        'template': template
    }),
    extensions=[EscapeExtension(), CoreExtension()]
)
engine.global_vars.update({'e': escape})


# test
class TestCase(unittest.TestCase):

    def test_render(self):
        template = engine.get_template('template')
        r = template.render({'var': '<X>'})
        self.assertEqual(
            '&lt;X&gt; &lt;X&gt; <X>   <meta name="&lt;X&gt;" />',
            r.strip())
        r = template.render({'var': 'X'})
        self.assertEqual(
            'X X X   <meta name="X" />',
            r.strip())


if __name__ == '__main__':
    unittest.main()
