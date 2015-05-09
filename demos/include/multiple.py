""" Demo: `page_a` and `page_b` are included into `page_all`.

    Note: inheritance chains do not intersect.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader


master_a = """
@def content_a():
@end

@content_a()
"""

page_a = """
@extends('master_a')

@def content_a():
  a
@end
"""

master_b = """
@def content_b():
@end

@content_b()
"""

page_b = """
@extends('master_b')

@def content_b():
  b
@end
"""

page_all = """
@include('page_a')
@include('page_b')
"""

pages = {
    'master_a': master_a,
    'master_b': master_b,
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
