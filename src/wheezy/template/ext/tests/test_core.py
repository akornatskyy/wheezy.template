
""" Unit tests for ``wheezy.templates.ext.core``.
"""

import unittest


class CleanSourceTestCase(unittest.TestCase):
    """ Test the ``clean_source``.
    """

    def test_new_line(self):
        """ Replace windows new line with linux new line.
        """
        from wheezy.template.ext.core import clean_source
        assert 'a\nb' == clean_source('a\r\nb')

    def test_leading_whitespace(self):
        """ Remove leading whitespace before @ symbol.
        """
        from wheezy.template.ext.core import clean_source
        assert 'a\n@b' == clean_source('a\n  @b')
        assert '@b' == clean_source('  @b')

    def test_ignore(self):
        """ Ignore double @.
        """
        from wheezy.template.ext.core import clean_source
        assert 'a\n  @@b' == clean_source('a\n  @@b')
        assert '  @@b' == clean_source('  @@b')


class LexerTestCase(unittest.TestCase):
    """ Test the ``CoreExtension`` lexers.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        self.engine = Engine(extensions=[CoreExtension()])

    def tokenize(self, source):
        return self.engine.lexer.tokenize(source)

    def test_stmt_token(self):
        """ Test statement token.
        """
        tokens = self.tokenize('@require(title, users)\n')
        assert (1, 'require', 'require(title, users)') == tokens[0]

    def test_var_token(self):
        """ Test variable token.
        """
        tokens = self.tokenize('@user.name ')
        assert (1, 'var', 'user.name') == tokens[0]
        tokens = self.tokenize('@user.pref[i].fmt() ')
        assert (1, 'var', 'user.pref[i].fmt()') == tokens[0]

    def test_markup_token(self):
        """ Test markup token.
        """
        tokens = self.tokenize(' test ')
        assert 1 == len(tokens)
        assert (1, 'markup', ' test ') == tokens[0]

    def test_markup_token_escape(self):
        """ Test markup token with escape.
        """
        tokens = self.tokenize('support@@acme.org')
        assert 1 == len(tokens)
        assert (1, 'markup', 'support@acme.org') == tokens[0]


class ParserTestCase(unittest.TestCase):
    """ Test the ``CoreExtension`` parsers.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        self.engine = Engine(extensions=[CoreExtension()])

    def parse(self, source):
        return list(self.engine.parser.parse(
            self.engine.lexer.tokenize(source)))

    def test_require(self):
        """ Test parse_require.
        """
        nodes = self.parse('@require(title, users)\n')
        assert [(1, 'require', ['title', 'users'])] == nodes

    def test_extends(self):
        """ Test parse_extends.
        """
        nodes = self.parse('@extends("shared/master.html")\n')
        assert [(1, 'extends', '"shared/master.html"')] == nodes

    def test_include(self):
        """ Test parse_include.
        """
        nodes = self.parse('@include("shared/scripts.html")\n')
        assert [(1, 'out', [
                    (1, 'include', '"shared/scripts.html"')
                ])] == nodes

    def test_markup(self):
        """ Test parse_markup.
        """
        nodes = self.parse("""
 Welcome, @name!
""")
        assert [(1, 'out', [
                    (1, 'markup', "'\\n Welcome, '"),
                    (2, 'var', 'name'),
                    (2, 'markup', "'!\\n'")
                ])] == nodes


class BuilderTestCase(unittest.TestCase):
    """ Test the ``CoreExtension`` generators.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        self.engine = Engine(extensions=[CoreExtension()])

    def build_source(self, source):
        nodes = list(self.engine.parser.parse(
                    self.engine.lexer.tokenize(source)))
        return self.engine.builder.build_source(nodes)

    def build_render(self, source):
        nodes = list(self.engine.parser.parse(
                    self.engine.lexer.tokenize(source)))
        return self.engine.builder.build_render(nodes)

    def build_extends(self, name, source):
        nodes = list(self.engine.parser.parse(
                    self.engine.lexer.tokenize(source)))
        return self.engine.builder.build_extends(name, nodes)

    def test_out(self):
        """ Test build_out.
        """
        assert "w('Welcome, '); w(username); w('!')" == self.build_source(
                'Welcome, @username!')
        assert """\
w('\\n<i>\\n')

w(username); w('\\n</i>')""" == self.build_source("""
<i>
    @username
</i>""")

    def test_if(self):
        """ Test if elif else statements.
        """
        assert """\
if n > 0:
    w('    Positive\\n')
elif n == 0:
    w('    Zero\\n')
else:
    w('    Negative\\n')""" == self.build_source("""\
@if n > 0:
    Positive
@elif n == 0:
    Zero
@else:
    Negative
@end
""")

    def test_def(self):
        """ Test def statement.
        """
        assert """\
def link(url, text):
    _b = []; w = _b.append; w('        <a href="'); w(url); \
w('">'); w(text); w('</a>\\n'); return ''.join(_b)
local_defs['link'] = link
w('    Please '); w(link('/en/signin', 'sign in')); w('.\\n')\
""" == self.build_source("""\
    @def link(url, text):
        <a href="@url">@text</a>
    @end
    Please @link('/en/signin', 'sign in').
""")

    def test_render(self):
        """ Test build_render.
        """
        assert """\
def render(ctx, local_defs, super_defs):
    _b = []; w = _b.append
    w('Hello')
    return ''.join(_b)""" == self.build_render("Hello")

    def test_extends(self):
        """ Test build_extends.
        """
        assert """\
def render(ctx, local_defs, super_defs):
    _b = []; w = _b.append
    w('Hello')
    return includes["base.html"](ctx, local_defs, super_defs)\
""" == self.build_extends('"base.html"', 'Hello')
