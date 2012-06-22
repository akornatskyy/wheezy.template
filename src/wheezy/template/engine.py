
"""
"""

from wheezy.template.builder import SourceBuilder
from wheezy.template.builder import builder_scan
from wheezy.template.comp import allocate_lock
from wheezy.template.comp import compile_source
from wheezy.template.lexer import Lexer
from wheezy.template.lexer import lexer_scan
from wheezy.template.parser import Parser
from wheezy.template.parser import parser_scan


class Engine(object):

    def __init__(self, loader, extensions, template_class=None):
        self.templates = {}
        self.renders = {}
        self.loader = loader
        self.template_class = template_class or Template
        self.lock = allocate_lock()
        lexer_rules, preprocessors = lexer_scan(extensions)
        self.lexer = Lexer(lexer_rules, preprocessors)
        parser_rules, parser_configs = parser_scan(extensions)
        self.parser = Parser(parser_rules, parser_configs)
        builder_rules = builder_scan(extensions)
        self.builder = SourceBuilder(builder_rules)
        self.global_vars = {'_r': self.get_render}

    def get_template(self, name):
        try:
            return self.templates[name]
        except KeyError:
            self.compile_template(name)
            return self.templates[name]

    def get_render(self, name):
        try:
            return self.renders[name]
        except KeyError:
            self.compile_template(name)
            return self.renders[name]

    # region: internal details

    def compile_template(self, name):
        self.lock.acquire(1)
        try:
            if name not in self.renders:
                template_source = self.loader.load(name)
                tokens = self.lexer.tokenize(template_source)
                nodes = list(self.parser.parse(tokens))
                #from pprint import pprint
                #pprint(nodes)
                module_source = self.builder.build_render(nodes)
                #from wheezy.template.utils import print_source
                #print_source(module_source, -1)
                render_template = compile_source(
                    module_source, name, self.global_vars, -2)
                self.renders[name] = render_template
                self.templates[name] = self.template_class(
                        name, render_template)
        finally:
            self.lock.release()


class Template(object):

    def __init__(self, name, render_template):
        self.name = name
        self.render_template = render_template

    def render(self, ctx):
        return self.render_template(ctx, {}, {})
