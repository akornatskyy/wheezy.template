import ast
import typing
from _thread import allocate_lock  # noqa

Tuple: typing.Any = tuple
List: typing.Any = list

# Marks a generated line that has no counterpart in the template source.
EXTRA_LINE = "  # wheezy.template: extra line"


def adjust_source_lineno(source: str, name: str, lineno: int) -> ast.Module:
    node = compile(source, name, "exec", ast.PyCF_ONLY_AST)
    extra_lines = [
        i
        for i, line in enumerate(source.split("\n"), 1)
        if line.endswith(EXTRA_LINE)
    ]
    # Align line numbers with the template source: apply the offset and
    # drop the extra lines. The offset moves the generated header to
    # lines < 1, which compile() rejects since python 3.11. Move such
    # nodes to line 1.
    for n in ast.walk(node):
        for line_attr, col_attr in (
            ("lineno", "col_offset"),
            ("end_lineno", "end_col_offset"),
        ):
            ln = getattr(n, line_attr, None)
            if ln is None:
                continue
            ln += lineno - sum(x < ln for x in extra_lines)
            if ln < 1:
                ln = 1
                setattr(n, col_attr, 0)
            setattr(n, line_attr, ln)
    return typing.cast(ast.Module, node)


__all__ = (
    "EXTRA_LINE",
    "List",
    "Tuple",
    "adjust_source_lineno",
)
