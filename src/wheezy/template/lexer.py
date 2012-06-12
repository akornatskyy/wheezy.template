
"""
"""

import re


class Lexer(object):

    def __init__(self, rules):
        self.rules = rules

    def tokenize(self, source):
        source = clean_source(source)
        tokens = [] ; append = tokens.append
        pos = 0 ; lineno = 1 ; end = len(source)
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


# region: utils

RE_CLEAN1 = re.compile('^([ ]+)@(?!@)', re.S)
RE_CLEAN2 = re.compile('\n([ ]+)@(?!@)', re.S)

def clean_source(source):
    return RE_CLEAN2.sub('\n@', RE_CLEAN1.sub('@',
        source.replace('\r\n', '\n')))


def find_all_balanced(text, start=0):
    if start >= len(text) or text[start] not in '([':
        return start
    while(1):
        pos = find_balanced(text, start)
        pos = find_balanced(text, pos, '[', ']')
        if pos != start:
            start = pos
        else:
            return pos


def find_balanced(text, start=0, start_sep='(', end_sep=')'):
    if start >= len(text) or start_sep != text[start]:
        return start
    balanced = 1
    pos = start + 1
    while pos < len(text):
        token = text[pos]
        pos += 1
        if token == end_sep:
            if balanced == 1:
                return pos
            balanced -= 1
        elif token == start_sep:
            balanced += 1
    return start
