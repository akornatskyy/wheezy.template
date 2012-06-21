
"""
"""

from wheezy.template.builder import SourceBuilder
from wheezy.template.builder import builder_scan
from wheezy.template.comp import compile_source
from wheezy.template.lexer import Lexer
from wheezy.template.lexer import lexer_scan
from wheezy.template.parser import Parser
from wheezy.template.parser import parser_scan


class Engine(object):

    def __init__(self, loader, extensions):
        lexer_rules, preprocessors = lexer_scan(extensions)
        self.lexer = Lexer(lexer_rules, preprocessors)
        parser_rules, parser_configs = parser_scan(extensions)
        self.parser = Parser(parser_rules, parser_configs)
        builder_rules = builder_scan(extensions)
        self.builder = SourceBuilder(builder_rules)
        self.loader = loader
        self.templates = {}

    def get_template(self, name):
        try:
            return self.templates[name]
        except KeyError:
            self.templates[name] = template = self.compile_template(name)
            return template

    def compile_template(self, name):
        template_source = self.loader.load(name)
        tokens = self.lexer.tokenize(template_source)
        nodes = list(self.parser.parse(tokens))
        from pprint import pprint
        pprint(nodes)
        module_source = self.builder.build_render(nodes)
        from wheezy.template.utils import print_source
        print_source(module_source, -1)
        global_vars = {}
        return Template(compile_source(
            module_source, name, global_vars, -2))


class Template(object):

    def __init__(self, render_template):
        self.render_template = render_template

    def render(self, ctx):
        local_defs = {}
        super_defs = {}
        return self.render_template(ctx, local_defs, super_defs)
