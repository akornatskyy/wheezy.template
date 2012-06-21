
"""
"""


def find_all_balanced(text, start=0):
    """ Finds balanced ``([`` with ``])`` assuming
        that ``start`` is pointing to ``(`` or ``[`` in ``text``.
    """
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
    """ Finds balanced ``start_sep`` with ``end_sep`` assuming
        that ``start`` is pointing to ``start_sep`` in ``text``.
    """
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


def print_source(source, lineno=1):  # pragma: nocover
    lines = []
    for line in source.split('\n'):
        lines.append("%02d " % lineno + line)
        lineno += line.count('\n') + 1
    print('\n'.join(lines))
