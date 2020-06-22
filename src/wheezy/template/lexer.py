
"""
"""


def lexer_scan(extensions):
    """ Scans extensions for ``lexer_rules`` and ``preprocessors``
        attributes.
    """
    lexer_rules = {}
    preprocessors = []
    postprocessors = []
    for extension in extensions:
        if hasattr(extension, 'lexer_rules'):
            lexer_rules.update(extension.lexer_rules)
        if hasattr(extension, 'preprocessors'):
            preprocessors.extend(extension.preprocessors)
        if hasattr(extension, 'postprocessors'):
            postprocessors.extend(extension.postprocessors)
    return {
        'lexer_rules': [lexer_rules[k] for k in sorted(lexer_rules.keys())],
        'preprocessors': preprocessors,
        'postprocessors': postprocessors
    }


class Lexer(object):
    """ Tokenizes input source per rules supplied.
    """

    def __init__(self, lexer_rules, preprocessors=None, postprocessors=None,
                 **ignore):
        """ Initializes with ``rules``. Rules must be a list of
            two elements tuple: ``(regex, tokenizer)`` where
            tokenizer if a callable of the following contract::

            def tokenizer(match):
                return end_index, token, value
        """
        self.rules = lexer_rules
        self.preprocessors = preprocessors or []
        self.postprocessors = postprocessors or []

    def tokenize(self, source):
        """ Translates ``source`` accoring to lexer rules into
            an iteratable of tokens.
        """
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
                    assert npos > pos
                    append((lineno, token, value))
                    lineno += source[pos:npos].count('\n')
                    pos = npos
                    break
            else:
                raise AssertionError('Lexer pattern mismatch.')
        for postprocessor in self.postprocessors:
            postprocessor(tokens)
        return tokens
