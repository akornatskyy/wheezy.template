""" Unit tests for ``wheezy.templates.ext.code``.
"""

import unittest


class LexerTestCase(unittest.TestCase):
    """ Test the ``CodeExtension`` lexers.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.code import CodeExtension
        from wheezy.template.loader import DictLoader

        self.engine = Engine(
            loader=DictLoader({}), extensions=[CodeExtension()]
        )

    def tokenize(self, source):
        return self.engine.lexer.tokenize(source)

    def test_code_token(self):
        """ Test code token.
        """
        tokens = self.tokenize("\n @(i = 1)")
        assert 1 == len(tokens)
        assert (1, "code", "(i = 1)") == tokens[0]
        tokens = self.tokenize("@(i = 1)\n")
        assert (1, "code", "(i = 1)\n") == tokens[0]


class ParserTestCase(unittest.TestCase):
    """ Test the ``CodeExtension`` parsers.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.code import CodeExtension
        from wheezy.template.loader import DictLoader

        self.engine = Engine(
            loader=DictLoader({}), extensions=[CodeExtension()]
        )

    def parse(self, source):
        return list(
            self.engine.parser.parse(self.engine.lexer.tokenize(source))
        )

    def test_code_empty(self):
        """ Test parse_code.
        """
        nodes = self.parse("@()")
        assert [(1, "code", [""])] == nodes

    def test_code(self):
        """ Test parse_code.
        """
        nodes = self.parse("@(i = 1)")
        assert [(1, "code", ["i = 1"])] == nodes

    def test_code_multiline(self):
        """ Test parse_code multiline.
        """
        nodes = self.parse(
            """\
@(
    i = 1
    j = 0
)
"""
        )
        assert [(1, "code", ["", "i = 1", "j = 0", ""])] == nodes


class BuilderTestCase(unittest.TestCase):
    """ Test the ``CodeExtension`` generators.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.code import CodeExtension
        from wheezy.template.loader import DictLoader

        self.engine = Engine(
            loader=DictLoader({}), extensions=[CodeExtension()]
        )

    def build_source(self, source):
        nodes = list(
            self.engine.parser.parse(self.engine.lexer.tokenize(source))
        )
        return self.engine.builder.build_source(nodes)

    def test_code(self):
        assert "i = 1" == self.build_source("@(i = 1)")
        assert "i = 1 " == self.build_source("@( i = 1 )")

    def test_code_multiline(self):
        assert """\

i = 1
j = 0
""" == self.build_source(
            """\
@(
    i = 1
    j = 0
)
"""
        )

    def test_code_with_indent(self):
        assert """\

def x():
    return 'x'
""" == self.build_source(
            """\
@(
    def x():
        return 'x'
)"""
        )


class TemplateTestCase(unittest.TestCase):
    """ Test the ``CodeExtension`` compiled templates.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.code import CodeExtension
        from wheezy.template.ext.core import CoreExtension
        from wheezy.template.loader import DictLoader

        self.templates = {}
        self.engine = Engine(
            loader=DictLoader(templates=self.templates),
            extensions=[CoreExtension(), CodeExtension()],
        )

    def render(self, source):
        self.templates["test.html"] = source
        template = self.engine.get_template("test.html")
        return template.render({})

    def test_code_single_line(self):
        assert "1" == self.render("@(i = 1)@i!s")

    def test_code_continue_newline(self):
        assert "1" == self.render("@(i = 1)\\\n@i!s")

    def test_code_separated_lines(self):
        assert "\n1" == self.render("@(i = 1)\n@i!s")

    def test_code_with_markup1(self):
        assert "x = 1" == self.render("x@(i = 1) = @i!s")

    def test_code_with_markup2(self):
        assert "x = 1" == self.render("x @(i = 1)= @i!s")

    def test_code_multiline(self):
        assert "x = 1" == self.render(
            """\
x \
@(
    i = 1
)\
= @i!s"""
        )
