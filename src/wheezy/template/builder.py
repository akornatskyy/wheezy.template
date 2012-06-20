
"""
"""


def builder_scan(extensions):
    builder_rules = {}
    for extension in extensions:
        if hasattr(extension, 'builder_rules'):
            rules = extension.builder_rules
            for token, builder in rules:
                builder_rules.setdefault(token, []).append(builder)
    return builder_rules


class BlockBuilder(object):

    def __init__(self, rules, indent='', lineno=0):
        self.rules = rules
        self.indent = indent
        self.lineno = lineno
        self.buf = []

    def start_block(self):
        self.indent += '    '

    def end_block(self):
        self.indent = self.indent[:-4]

    def add(self, lineno, code):
        if lineno < self.lineno:
            raise ValueError('Inconsistence at %s : %s' %
                    (self.lineno, lineno))
        if lineno == self.lineno:
            line = self.buf[-1]
            if line:
                self.buf[-1] = line + '; ' + code
            else:
                self.buf[-1] = code
        else:
            pad = lineno - self.lineno - 1
            if pad > 0:
                self.buf.extend([''] * pad)
            self.buf.append(self.indent + code)
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
            raise ValueError('No rule to build "%s" token.' % token)

    def to_string(self):
        return '\n'.join(self.buf)


class SourceBuilder(object):

    def __init__(self, rules, offset=2):
        self.rules = rules
        self.lineno = 0 - offset

    def build_source(self, nodes):
        block_builder = BlockBuilder(self.rules)
        block_builder.build_block(nodes)
        return block_builder.to_string()

    def build_render(self, nodes):
        block_builder = BlockBuilder(self.rules, lineno=self.lineno)
        block_builder.build_token(self.lineno + 1, 'render', nodes)
        return block_builder.to_string()

    def build_extends(self, name, nodes):
        block_builder = BlockBuilder(self.rules, lineno=self.lineno)
        block_builder.build_token(self.lineno + 1, 'extends',
                (name, nodes))
        return block_builder.to_string()
