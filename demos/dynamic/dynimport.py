""" Dynamically import a page.
"""

import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader

widgets_a = """
@def say_hi(name):
    Hi, @name.
@end
"""

widgets_b = """
@def say_hi(name):
    Hello, @name.
@end
"""

page_a = """
@require(widgets_impl)
@import 'widgets_' + widgets_impl as widget

@widget.say_hi('World')
"""

page_b = """
@require(widgets_impl)
@from 'widgets_' + widgets_impl import say_hi

@say_hi('World')
"""

page_c = """
@require(widgets_impl)
@from 'widgets_' + widgets_impl import say_hi as hi

@hi('World')
"""

pages = {
    "widgets_a": widgets_a,
    "widgets_b": widgets_b,
    "page_a": page_a,
    "page_b": page_b,
    "page_c": page_c,
}

engine = Engine(loader=DictLoader(pages), extensions=[CoreExtension()])


class TestCase(unittest.TestCase):
    def test_render(self) -> None:
        for page in ("page_a", "page_b", "page_c"):
            template = engine.get_template(page)
            r = template.render({"widgets_impl": "a"})
            self.assertEqual("Hi, World.", r.strip())
            r = template.render({"widgets_impl": "b"})
            self.assertEqual("Hello, World.", r.strip())


if __name__ == "__main__":
    unittest.main()
