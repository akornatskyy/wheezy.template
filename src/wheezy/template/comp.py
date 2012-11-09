
""" ``comp`` module.
"""

import sys


PY3 = sys.version_info[0] >= 3


if PY3:  # pragma: nocover
    from _thread import allocate_lock
else:  # pragma: nocover
    from thread import allocate_lock  # noqa


try:  # pragma: nocover
    import ast

    def adjust_source_lineno(source, name, lineno):
        source = compile(source, name, 'exec', ast.PyCF_ONLY_AST)
        ast.increment_lineno(source, lineno)
        return source

except ImportError:  # pragma: nocover

    def adjust_source_lineno(source, name, lineno):  # noqa
        return source
