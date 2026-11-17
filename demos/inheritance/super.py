"""Custom directive `super` to include a parent placeholder content."""

import re
import typing
import unittest
from collections.abc import Mapping

from wheezy.template.engine import Engine as BaseEngine
from wheezy.template.ext.core import CoreExtension, var_token
from wheezy.template.loader import DictLoader
from wheezy.template.typing import Token

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

pages = {"master": master, "page_a": page_a, "page_b": page_b}


class Engine(BaseEngine):
    def render(  # type: ignore[override]
        self,
        name: str,
        ctx: Mapping[str, typing.Any],
        local_defs: Mapping[str, typing.Any],
        super_defs: dict[str, typing.Any],
    ) -> str:
        s: Mapping[str, typing.Any] = {}
        super_defs["__super__"] = s
        return super().render(name, ctx, local_defs, s)


def super_token(m: re.Match[str]) -> Token:
    i = m.end(1) - m.start(1)
    end, _, value = var_token(m)
    s = 'super_defs["__super__"]["' + value[:i] + '"]' + value[i:]
    return end, "var", s


core = CoreExtension()
core.lexer_rules[150] = (re.compile(r"@super\.(\w+)"), super_token)

engine = Engine(loader=DictLoader(pages), extensions=[core])


class TestCase(unittest.TestCase):
    def test_render(self) -> None:
        template = engine.get_template("page_b")
        r = template.render({})
        assert ["b", "a", "super"] == r.split()


if __name__ == "__main__":
    unittest.main()
