""" Demo: `page_a` and `page_b` are rendered into `page_all`.

    Note: both `page_a` and `page_b` extend same `master`, inheritance
    chains intersect at `content` placeholder.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader


master = """
@def content():
@end

@content()
"""

page_a = """
@extends('master')

@def content():
  a
@end
"""

page_b = """
@extends('master')

@def content():
  b
@end
"""

page_all = """
@_r('page_a', ctx, {}, {})
@_r('page_b', ctx, {}, {})
"""

pages = {
    'master': master,
    'page_a': page_a,
    'page_b': page_b,
    'page_all': page_all
}

engine = Engine(
    loader=DictLoader(pages),
    extensions=[CoreExtension()]
)


class TestCase(unittest.TestCase):

    def test_render(self):
        template = engine.get_template('page_all')
        r = template.render({})
        self.assertEqual(['a', 'b'], r.split())


if __name__ == '__main__':
    unittest.main()
