
"""
"""

from wheezy.template.lexer import Lexer
from wheezy.template.lexer import lexer_scan
from wheezy.template.parser import Parser
from wheezy.template.parser import parser_scan


class Engine(object):

    def __init__(self, extensions):
        lexer_rules, preprocessors = lexer_scan(extensions)
        self.lexer = Lexer(lexer_rules, preprocessors)
        parser_rules, parser_configs = parser_scan(extensions)
        self.parser = Parser(parser_rules, parser_configs)
