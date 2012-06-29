
"""
"""

import imp

from wheezy.template.comp import adjust_source_lineno


class Compiler(object):

    def __init__(self, global_vars, source_lineno):
        self.global_vars = global_vars
        self.source_lineno = source_lineno

    def compile_module(self, source, name):
        source = adjust_source_lineno(source, name, self.source_lineno)
        compiled = compile(source, name, 'exec')
        module = imp.new_module(name)
        module.__name__ = name
        module.__dict__.update(self.global_vars)
        exec(compiled, module.__dict__)
        return module

    def compile_source(self, source, name):
        source = adjust_source_lineno(source, name, self.source_lineno)
        compiled = compile(source, name, 'exec')
        local_vars = {}
        exec(compiled, self.global_vars, local_vars)
        return local_vars
