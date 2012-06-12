
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
    return m.end(), m.group(2), m.group(1)


RE_VAR = re.compile('(\.\w+)+')


def var_token(m):
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
    return m.end(), 'markup', m.group().replace('@@', '@')


# region: core extension

class CoreExtension(object):

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
