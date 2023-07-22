import ast
import sys
import typing
from _thread import allocate_lock  # noqa


def adjust_source_lineno(source: str, name: str, lineno: int) -> typing.Any:
    node = compile(source, name, "exec", ast.PyCF_ONLY_AST)
    ast.increment_lineno(node, lineno)
    return node


if sys.version_info <= (3, 9, 0):  # pragma: nocover
    from typing import List, Tuple
else:  # pragma: nocover
    Tuple = tuple  # type: ignore
    List = list  # type: ignore


__all__ = (
    "adjust_source_lineno",
    "Tuple",
    "List",
)
