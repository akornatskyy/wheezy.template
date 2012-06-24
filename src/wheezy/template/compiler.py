
"""
"""

import imp

from wheezy.template.comp import adjust_source_lineno


class Compiler(object):

    def __init__(self, global_vars, source_lineno):
        self.global_vars = global_vars
        self.source_lineno = source_lineno

    def compile_module(self, source, name):
        compiled = compile(source, name, 'exec')
        mod = imp.new_module(name)
        mod.__name__ = name
        mod.__dict__.update(self.global_vars)
        mod.__dict__.update({'local_defs': {}, 'super_defs': {}})
        exec(compiled, mod.__dict__)
        return mod

    def compile_source(self, source, name):
        source = adjust_source_lineno(source, name, self.source_lineno)
        compiled = compile(source, name, 'exec')
        local_vars = {}
        exec(compiled, self.global_vars, local_vars)
        return local_vars
