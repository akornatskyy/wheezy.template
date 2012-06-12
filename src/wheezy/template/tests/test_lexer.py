
""" Unit tests for ``wheezy.templates.lexer``.
"""

import unittest


class LexerTestCase(unittest.TestCase):
    """ Test the ``Lexer``.
    """

    def test_tokenize(self):
        """ Test with simple rules
        """
        import re
        from wheezy.template.lexer import Lexer
        def word_token(m):
            return m.end(), 'w', m.group()
        def blank_token(m):
            return m.end(), 'b', m.group()
        lexer = Lexer([
            (re.compile(r'\w+'), word_token),
            (re.compile(r'\s+'), blank_token),
        ])
        assert [(1, 'w', 'hello'),
                (1, 'b', '\n '),
                (2, 'w', 'world')
            ] == lexer.tokenize('hello\n world')

    def test_trivial(self):
        """ Empty rules and source
        """
        from wheezy.template.lexer import Lexer
        lexer = Lexer([])
        assert [] == lexer.tokenize('')

    def test_raises_error(self):
        """ If there is no match it raises AssertionError.
        """
        from wheezy.template.lexer import Lexer
        lexer = Lexer([])
        self.assertRaises(AssertionError, lambda: lexer.tokenize('test'))


class CleanSourceTestCase(unittest.TestCase):
    """ Test the ``clean_source``.
    """

    def test_new_line(self):
        """ Replace windows new line with linux new line.
        """
        from wheezy.template.lexer import clean_source
        assert 'a\nb' == clean_source('a\r\nb')

    def test_leading_whitespace(self):
        """ Remove leading whitespace before @ symbol.
        """
        from wheezy.template.lexer import clean_source
        assert 'a\n@b' == clean_source('a\n  @b')
        assert '@b' == clean_source('  @b')

    def test_ignore(self):
        """ Ignore double @.
        """
        from wheezy.template.lexer import clean_source
        assert 'a\n  @@b' == clean_source('a\n  @@b')
        assert '  @@b' == clean_source('  @@b')


class FindAllBalancedTestCase(unittest.TestCase):
    """ Test the ``find_all_balanced``.
    """

    def test_start_out(self):
        """ The start index is out of range.
        """
        from wheezy.template.lexer import find_all_balanced
        assert 10 == find_all_balanced('test', 10)

    def test_start_separator(self):
        """ If text doesn't start with ``([`` return.
        """
        from wheezy.template.lexer import find_all_balanced
        assert 0 == find_all_balanced('test([', 0)
        assert 3 == find_all_balanced('test([', 3)

    def test_not_balanced(self):
        """ Separators are not balanced.
        """
        from wheezy.template.lexer import find_all_balanced
        assert 4 == find_all_balanced('test(a, b', 4)
        assert 4 == find_all_balanced('test[a, b()', 4)

    def test_balanced(self):
        """ Separators are balanced.
        """
        from wheezy.template.lexer import find_all_balanced
        assert 10 == find_all_balanced('test(a, b)', 4)
        assert 13 == find_all_balanced('test(a, b)[0]', 4)
        assert 12 == find_all_balanced('test(a, b())', 4)
        assert 17 == find_all_balanced('test(a, b())[0]()', 4)


class FindBalancedTestCase(unittest.TestCase):
    """ Test the ``find_balanced``.
    """

    def test_start_out(self):
        """ The start index is out of range.
        """
        from wheezy.template.lexer import find_balanced
        assert 10 == find_balanced('test', 10)

    def test_start_separator(self):
        """ If text doesn't start with ``start_sep`` return.
        """
        from wheezy.template.lexer import find_balanced
        assert 0 == find_balanced('test(', 0)
        assert 3 == find_balanced('test(', 3)

    def test_not_balanced(self):
        """ Separators are not balanced.
        """
        from wheezy.template.lexer import find_balanced
        assert 4 == find_balanced('test(a, b', 4)
        assert 4 == find_balanced('test(a, b()', 4)

    def test_balanced(self):
        """ Separators are balanced.
        """
        from wheezy.template.lexer import find_balanced
        assert 10 == find_balanced('test(a, b)', 4)
        assert 12 == find_balanced('test(a, b())', 4)
