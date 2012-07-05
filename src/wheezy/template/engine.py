
"""
"""

from wheezy.template.builder import SourceBuilder
from wheezy.template.builder import builder_scan
from wheezy.template.comp import allocate_lock
from wheezy.template.lexer import Lexer
from wheezy.template.lexer import lexer_scan
from wheezy.template.parser import Parser
from wheezy.template.parser import parser_scan


class Engine(object):

    def __init__(self, loader, extensions, compiler_class=None):
        self.lock = allocate_lock()
        self.renders = {}
        self.modules = {}
        self.global_vars = {
            '_r': self.render,
            '_i': self.import_name
        }
        self.loader = loader
        if not compiler_class:
            from wheezy.template.compiler import Compiler as compiler_class
        self.compiler = compiler_class(self.global_vars, -2)
        self.lexer = Lexer(**lexer_scan(extensions))
        self.parser = Parser(**parser_scan(extensions))
        self.builder = SourceBuilder(**builder_scan(extensions))

    def render(self, name, ctx, local_defs, super_defs):
        try:
            return self.renders[name](ctx, local_defs, super_defs)
        except KeyError:
            self.compile_template(name, ctx)
            return self.renders[name](ctx, local_defs, super_defs)

    # region: internal details

    def import_name(self, name, ctx):
        try:
            return self.modules[name]
        except KeyError:
            self.compile_import(name, ctx)
            return self.modules[name]

    def compile_template(self, name, ctx):
        self.lock.acquire(1)
        try:
            if name not in self.renders:
                template_source = self.loader.load(name)
                if template_source is None:
                    raise IOError('Template "%s" not found.' % name)
                tokens = self.lexer.tokenize(template_source)
                nodes = self.parser.parse(tokens)
                source = self.builder.build_render(nodes)

                #self.print_debug(name, tokens, nodes, source)

                render_template = self.compiler.compile_source(
                    source, name)['render']
                self.renders[name] = render_template
        finally:
            self.lock.release()

    def compile_import(self, name, ctx):
        self.lock.acquire(1)
        try:
            if name not in self.modules:
                template_source = self.loader.load(name)
                if template_source is None:
                    raise IOError('Import "%s" not found.' % name)
                tokens = self.lexer.tokenize(template_source)
                nodes = self.parser.parse(tokens)
                source = self.builder.build_module(nodes)

                #self.print_debug(name, tokens, nodes, source)

                self.modules[name] = self.compiler.compile_module(
                    source, name)
        finally:
            self.lock.release()

    def print_debug(self, name, tokens, nodes, source):  # pragma: nocover
        print(name.center(80, '-'))
        from pprint import pprint
        #pprint(tokens)
        pprint(nodes)
        from wheezy.template.utils import print_source
        print_source(source, -1)


class Template(object):

    def __init__(self, name, engine):
        self.name = name
        self.render_template = engine.render

    def render(self, ctx):
        return self.render_template(self.name, ctx, {}, {})
