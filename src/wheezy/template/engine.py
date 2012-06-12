
"""
"""

from wheezy.template.lexer import Lexer
from wheezy.template.lexer import lexer_scan


class Engine(object):

    def __init__(self, extensions):
        lexer_rules, preprocessors = lexer_scan(extensions)
        self.lexer = Lexer(lexer_rules, preprocessors)
