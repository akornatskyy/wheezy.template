""" Demo: `content_b` of `page_a` is substituted via include from `page_b`
    while rendering `page_all`.
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

@def content_b():
@end

@def content_a():
  a
  @content_b()
@end
"""

page_b = """
@def content_b():
  b
@end
"""

page_all = """
@include('page_b')
@include('page_a')
"""

pages = {
    "master_a": master_a,
    "page_a": page_a,
    "page_b": page_b,
    "page_all": page_all,
}

engine = Engine(loader=DictLoader(pages), extensions=[CoreExtension()])


class TestCase(unittest.TestCase):
    def test_render(self) -> None:
        template = engine.get_template("page_all")
        r = template.render({})
        self.assertEqual(["a", "b"], r.split())


if __name__ == "__main__":
    unittest.main()
