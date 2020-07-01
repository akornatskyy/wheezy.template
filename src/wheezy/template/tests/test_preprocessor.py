""" Unit tests for ``wheezy.templates.preprocessor.Preprocessor``.
"""

import unittest


class PreprocessorTestCase(unittest.TestCase):
    """ Test the ``Preprocessor``.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        from wheezy.template.loader import DictLoader
        from wheezy.template.preprocessor import Preprocessor

        def runtime_engine_factory(loader):
            engine = Engine(loader=loader, extensions=[CoreExtension(),])
            return engine

        self.templates = {}
        engine = Engine(
            loader=DictLoader(templates=self.templates),
            extensions=[CoreExtension("#", line_join=None),],
        )
        self.engine = Preprocessor(
            runtime_engine_factory, engine, key_factory=lambda ctx: ""
        )

    def render(self, name, ctx):
        template = self.engine.get_template(name)
        return template.render(ctx)

    def test_render(self):
        self.templates[
            "test.html"
        ] = """\
#require(_)
@require(username)
#_('Welcome,') @username!"""

        assert "Welcome, John!" == self.render(
            "test.html", ctx={"_": lambda x: x, "username": "John"}
        )

    def test_extends(self):
        self.templates.update(
            {
                "master.html": """\
#require(_)
@def say_hi(name):
    #_('Hello,') @name!
@end
@say_hi('John')""",
                "tmpl.html": """\
#require(_)
@extends('master.html')
@def say_hi(name):
    #_('Hi,') @name!
@end
""",
            }
        )

        assert "    Hi, John!\n" == self.render(
            "tmpl.html", ctx={"_": lambda x: x,}
        )

    def test_remove(self):
        self.templates["test.html"] = "Hello"
        assert "Hello" == self.render("test.html", {})
        self.engine.remove("x")
