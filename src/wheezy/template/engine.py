"""
"""

from wheezy.template.builder import SourceBuilder, builder_scan
from wheezy.template.comp import allocate_lock
from wheezy.template.compiler import Compiler
from wheezy.template.lexer import Lexer, lexer_scan
from wheezy.template.parser import Parser, parser_scan


class Engine(object):
    """The core component of template engine."""

    def __init__(self, loader, extensions, global_vars=None, template_class=None):
        self.lock = allocate_lock()
        self.templates = {}
        self.renders = {}
        self.modules = {}
        if global_vars is None:
            global_vars = {}
        global_vars.update({"_r": self.render, "_i": self.import_name})
        self.global_vars = global_vars
        self.loader = loader
        self.template_class = template_class or Template
        self.compiler = Compiler(self.global_vars, -2)
        self.lexer = Lexer(**lexer_scan(extensions))
        self.parser = Parser(**parser_scan(extensions))
        self.builder = SourceBuilder(**builder_scan(extensions))

    def get_template(self, name):
        """Returns compiled template."""
        try:
            return self.templates[name]
        except KeyError:
            self.compile_template(name)
            return self.templates[name]

    def render(self, name, ctx, local_defs, super_defs):
        """Renders template by name in given context."""
        try:
            return self.renders[name](ctx, local_defs, super_defs)
        except KeyError:
            self.compile_template(name)
            return self.renders[name](ctx, local_defs, super_defs)

    def remove(self, name):
        """Removes given ``name`` from internal cache."""
        self.lock.acquire(1)
        try:
            if name in self.renders:
                del self.templates[name]
                del self.renders[name]
            if name in self.modules:
                del self.modules[name]
        finally:
            self.lock.release()

    # region: internal details

    def import_name(self, name, ctx, local_defs, super_defs):
        try:
            return self.modules[name](ctx, local_defs, super_defs)
        except KeyError:
            self.compile_import(name)
            return self.modules[name](ctx, local_defs, super_defs)

    def compile_template(self, name):
        self.lock.acquire(1)
        try:
            if name not in self.renders:
                template_source = self.loader.load(name)
                if template_source is None:
                    raise IOError('Template "%s" not found.' % name)
                tokens = self.lexer.tokenize(template_source)
                nodes = self.parser.parse(tokens)
                source = self.builder.build_render(nodes)

                # print_debug(name, tokens, nodes, source)

                try:
                    render_template = self.compiler.compile_source(
                        source, name
                    )["render"]
                except SyntaxError as e:
                    raise complement_syntax_error(e, template_source, source)

                self.renders[name] = render_template
                self.templates[name] = self.template_class(
                    name, render_template
                )
        finally:
            self.lock.release()

    def compile_import(self, name):
        self.lock.acquire(1)
        try:
            if name not in self.modules:
                template_source = self.loader.load(name)
                if template_source is None:
                    raise IOError('Import "%s" not found.' % name)
                tokens = self.lexer.tokenize(template_source)
                nodes = self.parser.parse(tokens)
                source = self.builder.build_module(nodes)

                # print_debug(name, tokens, nodes, source)

                try:
                    self.modules[name] = self.compiler.compile_source(
                        source, name
                    )["get_defs"]
                except SyntaxError as e:
                    raise complement_syntax_error(e, template_source, source)
        finally:
            self.lock.release()


class Template(object):
    """Simple template class."""

    __slots__ = ("name", "render_template")

    def __init__(self, name, render_template):
        self.name = name
        self.render_template = render_template

    def render(self, ctx):
        return self.render_template(ctx, {}, {})


# region: internal details


def print_debug(name, tokens, nodes, source):  # pragma: nocover
    print(name.center(80, "-"))
    from pprint import pprint

    # pprint(tokens)
    pprint(nodes)
    from wheezy.template.utils import print_source

    print_source(source, -1)


def complement_syntax_error(err, template_source, source):
    """Complements SyntaxError with template and source snippets,
    like one below:

    .. code-block:: none

        File "shared/snippet/widget.html", line 4
            if :

        template snippet:
        02 <h1>
        03     @msg!h
        04     @if :
        05         sd
        06     @end

        generated snippet:
        02     _b = []; w = _b.append; w('<h1>\\n    ')
        03     w(h(msg)); w('\\n')
        04     if :
        05         w('        sd\\n')
        06

            if :
            ^
        SyntaxError: invalid syntax

    """
    text = """\
%s
template snippet:
%s

generated snippet:
%s

    %s""" % (
        err.text,
        source_chunk(template_source, err.lineno - 2, 1),
        source_chunk(source, err.lineno, -1),
        err.text.strip(),
    )
    return err.__class__(
        err.msg, (err.filename, err.lineno - 2, err.offset, text)
    )


def source_chunk(source, lineno, offset, extra=2):
    lines = source.split("\n", lineno + extra)
    s = max(0, lineno - extra - 1)
    e = min(len(lines), lineno + extra)
    r = []
    for i in range(s, e):
        line = lines[i]
        r.append("  %02d %s" % (i + offset, line))
    return "\n".join(r)
