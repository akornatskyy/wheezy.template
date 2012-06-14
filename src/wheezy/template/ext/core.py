
"""
"""

import re

from wheezy.template.utils import find_all_balanced


# region: config

end_tokens = ['end']
continue_tokens = ['else', 'elif']
compound_tokens = ['for', 'if', 'def'] + continue_tokens
reserved_tokens = ['require', '#', 'extends', 'include']
all_tokens = end_tokens + compound_tokens + reserved_tokens
out_tokens = ['markup', 'var', 'include']


# region: preprocessors

RE_CLEAN1 = re.compile('^([ ]+)@(?!@)', re.S)
RE_CLEAN2 = re.compile('\n([ ]+)@(?!@)', re.S)


def clean_source(source):
    """ Cleans leading whitespace before @. Ignores escaped (@@).
    """
    return RE_CLEAN2.sub('\n@', RE_CLEAN1.sub('@',
        source.replace('\r\n', '\n')))


# region: lexer extensions

def stmt_token(m):
    """ Produces statement token.
    """
    return m.end(), m.group(2), m.group(1)


RE_VAR = re.compile('(\.\w+)+')


def var_token(m):
    """ Produces variable token.
    """
    start = m.start(1)
    pos = m.end()
    source = m.string
    while 1:
        end = find_all_balanced(source, pos)
        if pos == end:
            break
        m = RE_VAR.match(source, end)
        if not m:
            break
        pos = m.end()
    return end, 'var', source[start:end]


def markup_token(m):
    """ Produces markup token.
    """
    return m.end(), 'markup', m.group().replace('@@', '@')


# region: parser config

def configure_parser(parser):
    parser.end_tokens.extend(end_tokens)
    parser.continue_tokens.extend(continue_tokens)
    parser.compound_tokens.extend(compound_tokens)
    parser.out_tokens.extend(out_tokens)


# region: parser

def parse_require(value):
    return map(lambda s: s.strip(' '), value.rstrip()[8:-1].split(','))


def parse_extends(value):
    return value.rstrip()[8:-1]


def parse_include(value):
    return value.rstrip()[8:-1]


def parse_markup(value):
    return '"""' + repr(value.replace('\\\n', ''))[1:-1] + '"""'


# region: core extension

class CoreExtension(object):
    """ Includes basic statements, variables processing and markup.
    """

    lexer_rules = {
            100: (re.compile(r'@((%s).*?(?<!\\))\n'
                    % '|'.join(all_tokens), re.S),
                stmt_token),
            200: (re.compile(r'@(\w+(\.\w+)*)'),
                var_token),
            999: (re.compile(r'.*?(?=(?<!@)@(?!@))|.*', re.S),
                markup_token)
    }

    preprocessors = [clean_source]

    parser_rules = {
            'require': parse_require,
            'extends': parse_extends,
            'include': parse_include,
            'markup': parse_markup
    }

    parser_configs = [configure_parser]
