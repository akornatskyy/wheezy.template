
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
        from wheezy.template.loader import DictLoader
        self.engine = Engine(
            loader=DictLoader({}),
            extensions=[CoreExtension()])

    def tokenize(self, source):
        return self.engine.lexer.tokenize(source)

    def test_stmt_token(self):
        """ Test statement token.
        """
        tokens = self.tokenize('@require(title, users)\n')
        assert (1, 'require', 'require(title, users)') == tokens[0]

    def test_comment_token(self):
        """ Test statement token.
        """
        tokens = self.tokenize('@#ignore\\\n@end\n')
        assert (1, '#', '#ignore@end') == tokens[0]

    def test_var_token(self):
        """ Test variable token.
        """
        tokens = self.tokenize('@user.name ')
        assert (1, 'var', 'user.name') == tokens[0]
        tokens = self.tokenize('@user.pref[i].fmt() ')
        assert (1, 'var', 'user.pref[i].fmt()') == tokens[0]

    def test_var_token_filter(self):
        """ Test variable token filter.
        """
        tokens = self.tokenize('@user.age!s')
        assert (1, 'var', 'user.age!!s') == tokens[0]
        tokens = self.tokenize('@user.age!s!h')
        assert (1, 'var', 'user.age!!s!h') == tokens[0]
        # escape or ignore !
        tokens = self.tokenize('@user.age!s!')
        assert (1, 'var', 'user.age!!s') == tokens[0]
        tokens = self.tokenize('@user.age!!s')
        assert (1, 'var', 'user.age') == tokens[0]
        tokens = self.tokenize('@user! ')
        assert (1, 'var', 'user') == tokens[0]

    def test_markup_token(self):
        """ Test markup token.
        """
        tokens = self.tokenize(' test ')
        assert 1 == len(tokens)
        assert (1, 'markup', ' test ') == tokens[0]
        tokens = self.tokenize('x@n')
        assert (1, 'markup', 'x') == tokens[0]

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
        from wheezy.template.loader import DictLoader
        self.engine = Engine(
            loader=DictLoader({}),
            extensions=[CoreExtension()])

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
        assert [(1, 'extends', ('"shared/master.html"', []))] == nodes

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
            (2, 'var', ('name', None)),
            (2, 'markup', "'!\\n'")
        ])] == nodes

    def test_var(self):
        """ Test parse_markup.
        """
        nodes = self.parse("""@name!h!""")
        assert [(1, 'out', [
            (1, 'var', ('name', ['h'])),
            (1, 'markup', "'!'")
        ])] == nodes
        nodes = self.parse("""@name!s!h!""")
        assert [(1, 'out', [
            (1, 'var', ('name', ['s', 'h'])),
            (1, 'markup', "'!'")
        ])] == nodes


class BuilderTestCase(unittest.TestCase):
    """ Test the ``CoreExtension`` generators.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        from wheezy.template.loader import DictLoader
        self.engine = Engine(
            loader=DictLoader({}),
            extensions=[CoreExtension()])

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

    def test_markup(self):
        assert "w('Hello')" == self.build_source('Hello')

    def test_comment(self):
        assert """\
w('Hello')
# comment
w(' World')""" == self.build_source("""\
Hello\\
@# comment
 World""")

    def test_require(self):
        assert """\
title = ctx['title']; username = ctx['username']
w(username)""" == self.build_source("""\
@require(title, username)
@username""")

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

    def test_for(self):
        assert """\
for color in colors:
    w(color); w('\\n')""" == self.build_source("""\
@for color in colors:
    @color
@end
""")

    def test_def(self):
        """ Test def statement.
        """
        assert """\
def link(url, text):
    _b = []; w = _b.append; w('        <a href="'); w(url); \
w('">'); w(text); w('</a>\\n')
    return ''.join(_b)
super_defs['link'] = link; link = local_defs.setdefault('link', link)
w('    Please '); w(link('/en/signin', 'sign in')); w('.\\n')\
""" == self.build_source("""\
    @def link(url, text):
        <a href="@url">@text</a>
        @#ignore
    @end
    Please @link('/en/signin', 'sign in').
""")

    def test_def_empty(self):
        """ Test def statement.
        """
        assert """\
def title():return ''
super_defs['title'] = title; title = local_defs.setdefault('title', title)
w(title()); w('.')""" == self.build_source("""\
@def title():
@end
@title().""")

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
    return _r("base.html", ctx, local_defs, super_defs)\
""" == self.build_render("""\
@extends("base.html")
""")


class TemplateTestCase(unittest.TestCase):
    """ Test the ``CoreExtension`` compiled templates.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        from wheezy.template.loader import DictLoader
        self.templates = {}
        self.engine = Engine(
            loader=DictLoader(templates=self.templates),
            extensions=[CoreExtension()])

    def render(self, ctx, source):
        self.templates['test.html'] = source
        template = self.engine.get_template('test.html')
        return template.render(ctx)

    def test_markup(self):
        ctx = {}
        assert 'Hello' == self.render(ctx, 'Hello')

    def test_comment(self):
        assert 'Hello World' == self.render({}, """\
Hello\\
@# comment
 World""")

    def test_var(self):
        ctx = {
            'username': 'John'
        }
        assert 'Welcome, John!' == self.render(ctx, """\
@require(username)
Welcome, @username!""")

    def test_if(self):
        template = """\
@require(n)
@if n > 0:
    Positive\\
@elif n == 0:
    Zero\\
@else:
    Negative\\
@end
"""
        assert '    Positive' == self.render({'n': 1}, template)
        assert '    Zero' == self.render({'n': 0}, template)
        assert '    Negative' == self.render({'n': -1}, template)

    def test_for(self):
        ctx = {
            'colors': ['red', 'yellow']
        }
        assert 'red\nyellow\n' == self.render(ctx, """\
@require(colors)
@for color in colors:
    @color
@end
""")

    def test_def(self):
        assert 'Welcome, John!' == self.render({}, """\
@def welcome(name):
Welcome, @name!\\
@end
@welcome('John')""")

    def test_def_empty(self):
        assert '.' == self.render({}, """\
@def title():
@end
@title().""")

    def test_def_syntax_error_compound(self):
        self.assertRaises(SyntaxError, lambda: self.render({}, """\
@def welcome(name):
@if name:
Welcome, @name!\\
@end
@end
@welcome('John')"""))

    def test_def_no_syntax_error(self):
        assert 'Welcome, John!' == self.render({}, """\
@def welcome(name):
@#ignore
@if name:
Welcome, @name!\\
@end
@end
@welcome('John')""")


class MultiTemplateTestCase(unittest.TestCase):
    """ Test the ``CoreExtension`` compiled templates.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.ext.core import CoreExtension
        from wheezy.template.loader import DictLoader
        self.templates = {}
        self.engine = Engine(
            loader=DictLoader(templates=self.templates),
            extensions=[CoreExtension()])

    def render(self, name, ctx):
        template = self.engine.get_template(name)
        return template.render(ctx)

    def test_extends(self):
        self.templates.update({
            'master.html': """\
@def say_hi(name):
    Hello, @name!
@end
@say_hi('John')""",

            'tmpl.html': """\
@extends('master.html')
@def say_hi(name):
    Hi, @name!
@end
"""
        })
        assert '    Hi, John!\n' == self.render('tmpl.html', {})
        assert '    Hello, John!\n' == self.render('master.html', {})

    def test_super(self):
        self.templates.update({
            'master.html': """\
@def say_hi(name):
    Hello, @name!\
@end
@say_hi('John')""",

            'tmpl.html': """\
@extends('master.html')
@def say_hi(name):
    @super_defs['say_hi'](name)!!\
@end
"""
        })
        assert '    Hello, John!!!' == self.render('tmpl.html', {})

    def test_include(self):
        self.templates.update({
            'footer.html': """\
@require(name)
Thanks, @name""",

            'tmpl.html': """\
Welcome to my site.
@include('footer.html')
"""
        })
        ctx = {'name': 'John'}
        assert """\
Welcome to my site.
Thanks, John""" == self.render('tmpl.html', ctx)
        assert 'Thanks, John' == self.render('footer.html', ctx)

    def test_import(self):
        self.templates.update({
            'helpers.html': """\
@def say_hi(name):
Hi, @name\
@end""",

            'tmpl.html': """\
@import 'helpers.html' as helpers
@helpers.say_hi('John')"""
        })
        assert """\
Hi, John""" == self.render('tmpl.html', {})

    def test_import_dynamic(self):
        self.templates.update({
            'helpers.html': """\
@def say_hi(name):
Hi, @name\
@end""",

            'tmpl.html': """\
@require(helpers_impl)
@import helpers_impl as helpers
@helpers.say_hi('John')"""
        })
        assert """\
Hi, John""" == self.render('tmpl.html', {'helpers_impl': 'helpers.html'})

    def test_from_import(self):
        self.templates.update({
            'helpers.html': """\
@def say_hi(name):
Hi, @name\
@end""",

            'tmpl.html': """\
@from 'helpers.html' import say_hi
@say_hi('John')"""
        })
        assert """\
Hi, John""" == self.render('tmpl.html', {})

    def test_from_import_dynamic(self):
        self.templates.update({
            'helpers.html': """\
@def say_hi(name):
Hi, @name\
@end""",

            'tmpl.html': """\
@require(helpers_impl)
@from helpers_impl import say_hi
@say_hi('John')"""
        })
        assert """\
Hi, John""" == self.render('tmpl.html', {'helpers_impl': 'helpers.html'})

    def test_from_import_as(self):
        self.templates.update({
            'share/helpers.html': """\
@def say_hi(name):
Hi, @name\
@end""",

            'tmpl.html': """\
@from 'share/helpers.html' import say_hi as hi
@hi('John')"""
        })
        assert """\
Hi, John""" == self.render('tmpl.html', {})
