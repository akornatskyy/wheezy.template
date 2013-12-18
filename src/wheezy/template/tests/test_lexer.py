
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
        from wheezy.template.lexer import lexer_scan

        def word_token(m):
            return m.end(), 'w', m.group()

        def blank_token(m):
            return m.end(), 'b', m.group()

        def to_upper(s):
            return s.upper()

        def cleanup(tokens):
            for i in range(len(tokens)):
                t = tokens[i]
                if t[i] == 'b':
                    tokens[i] = (t[0], 'b', ' ')

        class Extension(object):
            lexer_rules = {
                100: (re.compile(r'\w+'), word_token),
                200: (re.compile(r'\s+'), blank_token)
            }
            preprocessors = [to_upper]
            postprocessors = [cleanup]

        lexer = Lexer(**lexer_scan([Extension]))
        assert [(1, 'w', 'HELLO'),
                (1, 'b', ' '),
                (2, 'w', 'WORLD')] == lexer.tokenize('hello\n world')

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
