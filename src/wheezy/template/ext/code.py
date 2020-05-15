
"""
"""

import re

from wheezy.template.utils import find_balanced


# region: lexer extensions

def code_token(m):
    source = m.string
    start = m.end()
    end = find_balanced(source, start)
    if source[end::1] == '\n':
        end += 1
    return end, 'code', source[start:end]


# region: parser

def parse_code(value):
    lines = value.rstrip('\n')[1:-1].split('\n')
    lines[0] = lines[0].lstrip()
    if len(lines) == 1:
        return lines
    line = lines[1]
    n = len(line) - len(line.lstrip())
    return [s[:n].lstrip() + s[n:] for s in lines]


# region: block_builders

def build_code(builder, lineno, token, lines):
    for line in lines:
        builder.add(lineno, line)
        lineno += 1
    return True


# region: core extension

class CodeExtension(object):
    """ Includes support for embedded python code.
    """

    def __init__(self, token_start='@'):

        self.lexer_rules = {
            300: (re.compile(r'\s*%s(?=\()' % token_start), code_token),
        }

    parser_rules = {
        'code': parse_code
    }

    builder_rules = [
        ('code', build_code)
    ]
