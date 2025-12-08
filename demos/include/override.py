"""Demo: overrides `include` directive.

Note: an alternative implementation for `render` demo.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader
from wheezy.template.typing import Builder

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
@include('page_a')
@include('page_b')
"""

pages = {
    "master": master,
    "page_a": page_a,
    "page_b": page_b,
    "page_all": page_all,
}


def build_include(
    builder: Builder, lineno: int, token: str, value: str
) -> bool:
    assert token == "include"
    builder.add(lineno, "w(_r(" + value + ", ctx, {}, {}))")
    return True


class MyExtention(object):
    builder_rules = [("include", build_include)]


engine = Engine(
    loader=DictLoader(pages), extensions=[MyExtention(), CoreExtension()]
)


class TestCase(unittest.TestCase):
    def test_render(self) -> None:
        template = engine.get_template("page_all")
        r = template.render({})
        self.assertEqual(["a", "b"], r.split())


if __name__ == "__main__":
    unittest.main()
