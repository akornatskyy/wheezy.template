
"""
"""


def lexer_scan(extensions):
    lexer_rules = {}
    preprocessors = []
    for extension in extensions:
        if hasattr(extension, 'lexer_rules'):
            lexer_rules.update(extension.lexer_rules)
        if hasattr(extension, 'preprocessors'):
            preprocessors.extend(extension.preprocessors)
    return ([lexer_rules[k] for k in sorted(lexer_rules.keys())],
            preprocessors)


class Lexer(object):
    """ Tokenizes input source per rules supplied.
    """

    def __init__(self, rules, preprocessors=None):
        """ Initializes with ``rules``. Rules must be a list of
            two elements tuple: ``(regex, tokenizer)`` where
            tokenizer if a callable of the following contract::

            def tokenizer(match):
                return end_index, token, value
        """
        self.rules = rules
        self.preprocessors = preprocessors or []

    def tokenize(self, source):
        for preprocessor in self.preprocessors:
            source = preprocessor(source)
        tokens = []
        append = tokens.append
        pos = 0
        lineno = 1
        end = len(source)
        while pos < end:
            for regex, tokenizer in self.rules:
                m = regex.match(source, pos, end)
                if m:
                    npos, token, value = tokenizer(m)
                    append((lineno, token, value))
                    lineno += source[pos:npos].count('\n')
                    pos = npos
                    break
            else:
                assert False, 'Lexer pattern mismatch.'
        return tokens
