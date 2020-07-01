""" Master page placeholders as an alternative for `super` directive.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader

master = """
@def content_a():
@end

@def content():
  @content_a()
  super
@end

@content()
"""

page_a = """
@extends('master')

@def content_b():
@end

@def content_a():
  @content_b()
  a
@end
"""

page_b = """
@extends('page_a')

@def content_b():
  b
@end
"""

pages = {"master": master, "page_a": page_a, "page_b": page_b}

engine = Engine(loader=DictLoader(pages), extensions=[CoreExtension()])


class TestCase(unittest.TestCase):
    def test_render(self):
        template = engine.get_template("page_b")
        r = template.render({})
        assert ["b", "a", "super"] == r.split()


if __name__ == "__main__":
    unittest.main()
