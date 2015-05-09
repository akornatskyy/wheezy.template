""" Dynamically extends a master page.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader


master_a = """
@def content():
@end

a
@content()
"""

master_b = """
@def content():
@end

b
@content()
"""

page = """
@require(name)
@extends('master_' + name)

@def content():
    page
@end
"""

pages = {
    'master_a': master_a,
    'master_b': master_b,
    'page': page,
}

engine = Engine(
    loader=DictLoader(pages),
    extensions=[CoreExtension()]
)


class TestCase(unittest.TestCase):

    def test_render(self):
        template = engine.get_template('page')
        r = template.render({'name': 'a'})
        self.assertEqual(['a', 'page'], r.split())
        r = template.render({'name': 'b'})
        self.assertEqual(['b', 'page'], r.split())


if __name__ == '__main__':
    unittest.main()
