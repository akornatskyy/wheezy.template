""" Custom HTML escape by default extension.
"""

import typing
import unittest

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import DictLoader
from wheezy.template.typing import Builder

try:
    from wheezy.html.utils import escape_html as escape
except ImportError:
    from html import escape


def build_var(
    builder: Builder, lineno: int, token: str, value: typing.Any
) -> bool:
    assert token == "var"
    var, var_filters = value
    if not var_filters:
        builder.add(lineno, "w(e(str(" + var + ")))")
        return True
    if "safe" in var_filters:
        builder.add(lineno, "w(" + var + ")")
        return True
    return False


class EscapeExtension(object):
    builder_rules = [("var", build_var)]


# setup
template = """
@require(var)
@def x(s):
  <meta name="@s" />
@end
@var @var!e @var!s @x(var)!safe
"""

engine = Engine(
    loader=DictLoader({"template": template}),
    extensions=[EscapeExtension(), CoreExtension()],
)
engine.global_vars.update({"e": escape})


# test
class TestCase(unittest.TestCase):
    def test_render(self) -> None:
        template = engine.get_template("template")
        r = template.render({"var": "<X>"})
        self.assertEqual(
            '&lt;X&gt; &lt;X&gt; <X>   <meta name="&lt;X&gt;" />', r.strip()
        )
        r = template.render({"var": "X"})
        self.assertEqual('X X X   <meta name="X" />', r.strip())


if __name__ == "__main__":
    unittest.main()
