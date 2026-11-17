import typing
from types import ModuleType

from wheezy.template.comp import adjust_source_lineno


class Compiler:
    def __init__(
        self, global_vars: dict[str, typing.Any], source_lineno: int
    ) -> None:
        self.global_vars = global_vars
        self.source_lineno = source_lineno

    def compile_module(self, source: str, name: str) -> ModuleType:
        node = adjust_source_lineno(source, name, self.source_lineno)
        compiled = compile(node, name, "exec")
        module = ModuleType(name)
        module.__name__ = name
        module.__dict__.update(self.global_vars)
        exec(compiled, module.__dict__)  # noqa: S102
        return module

    def compile_source(self, source: str, name: str) -> dict[str, typing.Any]:
        node = adjust_source_lineno(source, name, self.source_lineno)
        compiled = compile(node, name, "exec")
        local_vars: dict[str, typing.Any] = {}
        exec(compiled, self.global_vars, local_vars)  # noqa: S102
        return local_vars
