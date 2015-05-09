""" Dynamically include a page.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader


page_a = 'a'
page_b = 'b'

page_c = """
@require(name)
@include('page_' + name)
"""

pages = {
    'page_a': page_a,
    'page_b': page_b,
    'page_c': page_c
}

engine = Engine(
    loader=DictLoader(pages),
    extensions=[CoreExtension()]
)


class TestCase(unittest.TestCase):

    def test_render(self):
        template = engine.get_template('page_c')
        r = template.render({'name': 'a'})
        self.assertEqual('a', r.strip())
        r = template.render({'name': 'b'})
        self.assertEqual('b', r.strip())


if __name__ == '__main__':
    unittest.main()
