import ast
import typing
from _thread import allocate_lock  # noqa

Tuple: typing.Any = tuple
List: typing.Any = list


def adjust_source_lineno(source: str, name: str, lineno: int) -> ast.Module:
    node = compile(source, name, "exec", ast.PyCF_ONLY_AST)
    ast.increment_lineno(node, lineno)
    # The offset aligns line numbers with the template source, but it
    # moves the generated header to lines < 1, which compile() rejects
    # since python 3.11. Move such nodes to line 1.
    for n in ast.walk(node):
        if getattr(n, "lineno", 1) < 1:
            n.lineno, n.col_offset = 1, 0  # type: ignore[attr-defined]
        end_lineno = getattr(n, "end_lineno", None)
        if end_lineno is not None and end_lineno < 1:
            n.end_lineno, n.end_col_offset = 1, 0  # type: ignore[attr-defined]
    return typing.cast(ast.Module, node)


__all__ = (
    "List",
    "Tuple",
    "adjust_source_lineno",
)
