
"""
"""

import re

from wheezy.template.comp import PY3
from wheezy.template.utils import find_all_balanced


# region: config

end_tokens = ['end']
continue_tokens = ['else:', 'elif ']
compound_tokens = ['for ', 'if ', 'def ', 'extends'] + continue_tokens
reserved_tokens = ['require', '#', 'include']
all_tokens = end_tokens + compound_tokens + reserved_tokens
out_tokens = ['markup', 'var', 'include']
known_var_filters = {
        's': PY3 and 'str' or 'unicode'
}

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
    return m.end(), str(m.group(2)), str(m.group(1))


RE_VAR = re.compile('(\.\w+)+')
RE_VAR_FILTER = re.compile('(?<!!)!\w+(!\w+)*')


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
    value = str(source[start:end])
    m = RE_VAR_FILTER.match(source, end)
    if m:
        end = m.end()
        value += '!' + m.group()
    return end, 'var', value


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
    return [v.strip(' ') for v in value.rstrip()[8:-1].split(',')]


def parse_extends(value):
    return value.rstrip()[8:-1]


def parse_include(value):
    return value.rstrip()[8:-1]


def parse_var(value):
    if '!!' not in value:
        return value, None
    var, var_filter = value.rsplit('!!', 1)
    return var, var_filter.split('!')


def parse_markup(value):
    value = value.replace('\\\n', '')
    if value:
        return repr(value)
    else:
        return None


# region: block_builders

def build_extends(builder, lineno, token, nodes):
    assert token == 'render'
    if len(nodes) != 1:
        return False
    lineno, token, value = nodes[0]
    if token != 'extends':
        return False
    extends, nodes = value
    for lineno, token, value in nodes:
        if token in ('def ', 'require'):
            builder.build_token(lineno, token, value)
    lineno = builder.lineno
    builder.add(lineno + 1, 'return _r(' + extends +
            ', ctx, local_defs, super_defs)')
    return True


def build_render(builder, lineno, token, nodes):
    assert lineno <= 0
    assert token == 'render'
    builder.add(lineno, '_b = []; w = _b.append')
    builder.build_block(nodes)
    lineno = builder.lineno
    builder.add(lineno + 1, "return ''.join(_b)")
    return True


def build_def_empty(builder, lineno, token, value):
    assert token == 'def '
    stmt, nodes = value
    if nodes:
        return False
    def_name = stmt[4:stmt.index('(', 5)]
    builder.add(lineno, stmt)
    builder.start_block()
    builder.add(lineno, "return ''")
    builder.end_block()
    builder.add(lineno + 1, def_name.join([
        "super_defs['", "'] = ", "; ",
        " = local_defs.setdefault('", "', ", ")"
    ]))
    return True


def build_def(builder, lineno, token, value):
    assert token == 'def '
    stmt, nodes = value
    def_name = stmt[4:stmt.index('(', 5)]
    builder.add(lineno, stmt)
    builder.start_block()
    builder.add(lineno + 1, '_b = []; w = _b.append')
    builder.build_block(nodes)
    lineno = builder.lineno
    builder.add(lineno, "return ''.join(_b)")
    builder.end_block()
    builder.add(lineno + 1, def_name.join([
        "super_defs['", "'] = ", "; ",
        " = local_defs.setdefault('", "', ", ")"
    ]))
    return True


def build_out(builder, lineno, token, nodes):
    assert token == 'out'
    for lineno, token, value in nodes:
        if token == 'include':
            builder.add(lineno, 'w(' + '_r(' + value +
                ', ctx, local_defs, super_defs)' + ')')
        elif token == 'var':
            var, var_filters = value
            if var_filters:
                for f in reversed(var_filters):
                    var = known_var_filters.get(f, f) + '(' + var + ')'
            builder.add(lineno, 'w(' + var + ')')
        elif value:
            builder.add(lineno, 'w(' + value + ')')
    return True


def build_compound(builder, lineno, token, value):
    assert token in compound_tokens
    stmt, nodes = value
    builder.add(lineno, stmt)
    builder.start_block()
    builder.build_block(nodes)
    builder.end_block()
    return True


def build_require(builder, lineno, token, variables):
    builder.add(lineno, '; '.join([
                name + " = ctx['" + name + "']" for name in variables]))
    return True


def build_comment(builder, lineno, token, comment):
    builder.add(lineno, comment)
    return True


# region: core extension

class CoreExtension(object):
    """ Includes basic statements, variables processing and markup.
    """

    lexer_rules = {
            100: (re.compile(r'@((%s).*?(?<!\\))\n|$'
                    % '|'.join(all_tokens), re.S),
                stmt_token),
            200: (re.compile(r'@(\w+(\.\w+)*)'),
                var_token),
            999: (re.compile(r'.+?(?=(?<!@)@(?!@))|.+', re.S),
                markup_token),
    }

    preprocessors = [clean_source]

    parser_rules = {
            'require': parse_require,
            'extends': parse_extends,
            'include': parse_include,
            'var': parse_var,
            'markup': parse_markup,
    }

    parser_configs = [configure_parser]

    builder_rules = [
            ('render', build_extends),
            ('render', build_render),
            ('require', build_require),
            ('out', build_out),
            ('def ', build_def_empty),
            ('def ', build_def),
            ('if ', build_compound),
            ('elif ', build_compound),
            ('else:', build_compound),
            ('for ', build_compound),
            ('#', build_comment),
    ]
