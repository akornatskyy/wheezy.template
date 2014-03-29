
"""
"""


def builder_scan(extensions):
    builder_rules = {}
    for extension in extensions:
        if hasattr(extension, 'builder_rules'):
            rules = extension.builder_rules
            for token, builder in rules:
                builder_rules.setdefault(token, []).append(builder)
    return {
        'builder_rules': builder_rules
    }


class BlockBuilder(object):

    __slots__ = ('rules', 'indent', 'lineno', 'buf')

    def __init__(self, rules, indent='', lineno=0):
        self.rules = rules
        self.indent = indent
        self.lineno = lineno
        self.buf = []

    def start_block(self):
        self.indent += '    '

    def end_block(self):
        if len(self.indent) < 4:
            raise SyntaxError('Unexpected end of block.')
        self.indent = self.indent[:-4]

    def add(self, lineno, code):
        if lineno < self.lineno:
            raise SyntaxError('Inconsistence at %s : %s' %
                              (self.lineno, lineno))
        if lineno == self.lineno:
            line = self.buf[-1]
            if code:
                if line:
                    if line[-1:] == ':':
                        self.buf[-1] = line + code
                    else:
                        self.buf[-1] = line + '; ' + code
                else:
                    self.buf[-1] = self.indent + code
        else:
            pad = lineno - self.lineno - 1
            if pad > 0:
                self.buf.extend([''] * pad)
            if code:
                self.buf.append(self.indent + code)
            else:
                self.buf.append('')
        self.lineno = lineno + code.count('\n')

    def build_block(self, nodes):
        for lineno, token, value in nodes:
            self.build_token(lineno, token, value)

    def build_token(self, lineno, token, value):
        if token in self.rules:
            for rule in self.rules[token]:
                if rule(self, lineno, token, value):
                    break
        else:
            raise SyntaxError('No rule to build "%s" token at line %d.' %
                              (token, lineno))

    def to_string(self):
        return '\n'.join(self.buf)


class SourceBuilder(object):

    __slots__ = ('rules', 'lineno')

    def __init__(self, builder_rules, builder_offset=2, **ignore):
        self.rules = builder_rules
        self.lineno = 0 - builder_offset

    def build_source(self, nodes):
        builder = BlockBuilder(self.rules)
        builder.build_block(nodes)
        return builder.to_string()

    def build_render(self, nodes):
        builder = BlockBuilder(self.rules, lineno=self.lineno)
        builder.add(self.lineno + 1,
                    'def render(ctx, local_defs, super_defs):')
        builder.start_block()
        builder.build_token(self.lineno + 2, 'render', nodes)
        return builder.to_string()

    def build_module(self, nodes):
        builder = BlockBuilder(self.rules, lineno=self.lineno)
        builder.add(self.lineno + 1, 'local_defs = {}; super_defs = {}')
        builder.build_token(self.lineno + 2, 'module', nodes)
        return builder.to_string()
