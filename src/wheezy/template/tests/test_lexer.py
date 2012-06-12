
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
