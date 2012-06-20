
"""
"""


def parser_scan(extensions):
    parser_rules = {}
    configs = []
    for extension in extensions:
        if hasattr(extension, 'parser_rules'):
            parser_rules.update(extension.parser_rules)
        if hasattr(extension, 'parser_configs'):
            configs.extend(extension.parser_configs)
    return parser_rules, configs


class Parser(object):
    """
        ``continue_tokens`` are used to insert ``end`` node right
        before them to simulate a block end. Such nodes have token
        value ``None``.

        ``out_tokens`` are combined together into a single node.
    """

    def __init__(self, rules, configs=None):
        self.end_tokens = []
        self.continue_tokens = []
        self.compound_tokens = []
        self.out_tokens = []
        self.rules = rules
        if configs:
            for config in configs:
                config(self)

    def end_continue(self, tokens):
        """ If token is in ``continue_tokens`` prepend it
            with end token so it simulate a closed block.
        """
        for t in tokens:
            if t[1] in self.continue_tokens:
                yield (t[0], 'end', None)
            yield t

    def parse_iter(self, tokens):
        operands = []
        for lineno, token, value in tokens:
            if token in self.rules:
                value = self.rules[token](value)
            if token in self.out_tokens:
                operands.append((lineno, token, value))
            else:
                if operands:
                    yield operands[0][0], 'out', operands
                    operands = []
                if token in self.compound_tokens:
                    yield lineno, token, (
                            value, list(self.parse_iter(tokens)))
                else:
                    if token in self.end_tokens:
                        break
                    yield lineno, token, value
        if operands:
            yield operands[0][0], 'out', operands

    def parse(self, tokens):
        return self.parse_iter(self.end_continue(tokens))
