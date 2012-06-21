
""" ``comp`` module.
"""

import sys


PY3 = sys.version_info[0] >= 3

try:  # pragma: nocover
    import ast

    def compile_source(source, name, global_vars, lineno):
        source_tree = compile(source, name, 'exec', ast.PyCF_ONLY_AST)
        ast.increment_lineno(source_tree, lineno)
        compiled = compile(source_tree, name, 'exec')
        local_vars = {}
        exec(compiled, global_vars, local_vars)
        return local_vars['render']

except ImportError:  # pragma: nocover

    def compile_source(source, name, global_vars, lineno):
        compiled = compile(source, name, 'exec')
        local_vars = {}
        exec(compiled, global_vars, local_vars)
        return local_vars['render']
