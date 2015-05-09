""" Custom directive `super` to include a parent placeholder content.
"""

import re
import unittest

from wheezy.template.engine import Engine as BaseEngine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.ext.core import var_token
from wheezy.template.loader import DictLoader


master = """
@def content():
  super
@end

@content()
"""

page_a = """
@extends('master')

@def content():
  a

  @super.content()
@end
"""

page_b = """
@extends('page_a')

@def content():
  b

  @super.content()
@end
"""

pages = {
    'master': master,
    'page_a': page_a,
    'page_b': page_b
}


class Engine(BaseEngine):

    def render(self, name, ctx, local_defs, super_defs):
        super_defs['__super__'] = s = {}
        return super(Engine, self).render(name, ctx, local_defs, s)


def super_token(m):
    i = m.end(1) - m.start(1)
    end, name, value = var_token(m)
    s = 'super_defs["__super__"]["' + value[:i] + '"]' + value[i:]
    return end, 'var', s


core = CoreExtension()
core.lexer_rules[150] = (re.compile(r'@super\.(\w+)'), super_token)

engine = Engine(
    loader=DictLoader(pages),
    extensions=[core]
)


class TestCase(unittest.TestCase):

    def test_render(self):
        template = engine.get_template('page_b')
        r = template.render({})
        assert ['b', 'a', 'super'] == r.split()


if __name__ == '__main__':
    unittest.main()
